#!/usr/bin/env python3
''' ggac_surface.py
Author:     Connor Natzke
Date:       Mar 2021
Revision:   Oct 2023
Purpose:    Generate a Pegasus workflow for OSG submission
'''
# --- Configuration -----------------------------------------------------------
import logging
import os
import argparse as ap
from Pegasus.api import *
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

def create_workflow(args):
    # --- Working Directory Setup -------------------------------------------------
    # A good working directory for workflow runs and output files
    WORK_DIR = Path.home() / "projects/simulation-145mm-ggac"
    WORK_DIR.mkdir(exist_ok=True)

    TOP_DIR = Path(__file__).resolve().parents[1]

    # --- Properties --------------------------------------------------------------
    props = Properties()
    props["pegasus.monitord.encoding"] = "json"

    # Provide full kickstart record, including environment, even for successful jobs
    props["pegasus.gridstart.arguments"] = "-f"

    # Limit number of idle jobs
    #props["dagman.maxidle"] = "500"
    #props["dagman.maxjobs"] = "500"

    # turn off 'register_local' jobs, they are not necesary for my workflow since I don't reuse data.
    props["pegasus.register"] = "off"

    # Limit the number of transfer jobs so servers don't get overwhelmed
    # We need this line for cronos, otherwise it appears as a cyberattack
    #props["pegasus.stageout.clusters"] = "1000"
    props["dagman.stageout.maxjobs"] = "10"

    # Enable more cleanup jobs
    #props["pegasus.file.cleanup.clusters.num"] = "2000"

    # Set retry limit
    props["dagman.retry"] = "3"

    # Help Pegasus developers by sharing performance data
    props["pegasus.catalog.workflow.amqp.url"] = "amqp://friend:donatedata@msgs.pegasus.isi.edu:5672/prod/workflows"

    # Write properties file to ./pegasus.properties
    props.write()

    # --- Sites -------------------------------------------------------------------
    sc = SiteCatalog()

    # local site (submit node)
    local_site = Site(name="local", arch=Arch.X86_64)

    local_shared_scratch = Directory(
        directory_type=Directory.SHARED_SCRATCH, path=WORK_DIR / "scratch")
    local_shared_scratch.add_file_servers(FileServer(
        url="file://" + str(WORK_DIR / "scratch"), operation_type=Operation.ALL))
    local_site.add_directories(local_shared_scratch)

    local_site.add_env(PATH=os.environ["PATH"])
    local_site.add_profiles(Namespace.PEGASUS, key='SSH_PRIVATE_KEY',
                            value='/home/cnatzke/.ssh/id_rsa-pegasus')
    sc.add_sites(local_site)

    # condorpool (execution nodes)
    condorpool_site = Site(
        name="condorpool", arch=Arch.X86_64, os_type=OS.LINUX)
    condorpool_site.add_pegasus_profile(style="condor")
    condorpool_site.add_condor_profile(
        universe="vanilla",
        requirements="HAS_SINGULARITY == TRUE && OSG_HOST_KERNEL_VERSION >= 31000",
        request_cpus=1,
        request_memory="4 GB",
        request_disk="2 GB"
    )
    sc.add_sites(condorpool_site)

    # remote server (for analysis)
    remote_site = Site(
        name="remote", arch=Arch.X86_64, os_type=OS.LINUX)

    # build remote storage paths
    remote_storage_path = f'/data_fast/cnatzke/simulation-145mm-ggac/data/z{args.element}.a{args.isotope}/{args.gamma1}-{args.gamma2}'
    remote_storage_url = f'scp://cnatzke@cronos.mines.edu{remote_storage_path}'

    remote_storage = Directory(directory_type=Directory.LOCAL_STORAGE, path=remote_storage_path)
    remote_storage.add_file_servers(FileServer(url=remote_storage_url, operation_type=Operation.ALL))
    remote_site.add_directories(remote_storage)

    sc.add_sites(remote_site)

    # write SiteCatalog to ./sites.yml
    sc.write()

    # --- Transformations ---------------------------------------------------------
    simulation = Transformation(
        name="simulation",
        site="local",
        pfn=TOP_DIR / "bin/run_simulation.sh",
        is_stageable=True,
        arch=Arch.X86_64
    )

    data_processing = Transformation(
        name="data_processing",
        site="local",
        pfn=TOP_DIR / "bin/sort_and_fit_simulation_output.sh",
        is_stageable=True,
        arch=Arch.X86_64
    )

    merge = Transformation(
        name="merge",
        site="local",
        pfn=TOP_DIR / "bin/merge.sh",
        is_stageable=True,
        arch=Arch.X86_64
    )

    tc = TransformationCatalog()
    tc.add_transformations(simulation, data_processing, merge)
    # write TransformationCatalog to ./transformations.yml
    tc.write()

    # --- Replicas ----------------------------------------------------------------
    # Use all input files in "inputs" directory for given isotope
    input_files_dir = f"inputs/user-data/z{args.element}.a{args.isotope}.e{args.gamma1}_{args.gamma2}"
    input_files = [File(f.name) for f in (TOP_DIR / input_files_dir).iterdir()]

    rc = ReplicaCatalog()
    for f in input_files:
        rc.add_replica(site="local", lfn=f, pfn=TOP_DIR / input_files_dir / f.lfn)

    # write ReplicaCatalog to replicas.yml
    rc.write()

    # --- WorkFlow ----------------------------------------------------------------
    jobs = round(args.total_events / args.batch_size)
    z_list = ['z0', 'z2', 'z4']
    merge_limit = 50
    merge_job = None
    merge_id = 0
    merge_count = 0

    wf = Workflow(name=f'simulation-145mm-ggac')

    for z in z_list:
        for job in range(jobs):
            run_macro_filename = f'run_macro.{z}.mac'
            simulation_output_filename = f'g4out_{z}_{job:04d}.root'
            data_processing_output_filename = f'analysis_{z}_{job:04d}.root'
            out_file_histogram_name = f'histograms_{z}_{job:04d}.root'
            peak_areas_filename = f'peak_areas_{z}_{job:04d}.csv'


            simulation_job = Job(simulation)\
                .add_args(run_macro_filename, simulation_output_filename)\
                .add_inputs(*input_files)\
                .add_outputs(File(simulation_output_filename), stage_out=False)\
                .add_profiles(
                    Namespace.CONDOR,
                    key="+SingularityImage",
                    value='"/cvmfs/singularity.opensciencegrid.org/cnatzke/griffin_simulation:geant4.10.01"'
            )

            data_processing_job = Job(data_processing)\
                .add_args(simulation_output_filename, data_processing_output_filename, out_file_histogram_name, args.gamma1, args.gamma2, peak_areas_filename)\
                .add_inputs(File(simulation_output_filename), File("AngularCorrelationHelper.cxx"), File("AngularCorrelationHelper.hh"), File("processSimulationOutputOSG.C")) \
                .add_outputs(File(out_file_histogram_name), File(peak_areas_filename), stage_out=False)\
                .add_profiles(
                    Namespace.CONDOR,
                    key="+SingularityImage",
                    value='"osdf:///ospool/ap20/data/cnatzke/containers/processing_stack_v1.0.sif"'
                )

            wf.add_jobs(simulation_job)
            wf.add_jobs(data_processing_job)

            if merge_job is None:
                merge_job = Job(merge)\
                        .add_args(f'{merge_id}.tar.gz')\
                        .add_outputs(File(f'{merge_id}.tar.gz'))\
                        .add_profiles(
                            Namespace.CONDOR,
                            key="+SingularityImage",
                            value='"/cvmfs/singularity.opensciencegrid.org/cnatzke/prepare_files:latest"')
                merge_job.add_inputs(*input_files)
                merge_job.add_args(*input_files)

            merge_job.add_inputs(File(out_file_histogram_name))
            merge_job.add_args(File(out_file_histogram_name))
            merge_job.add_inputs(File(peak_areas_filename))
            merge_job.add_args(File(peak_areas_filename))
            merge_count += 1

            if merge_count == merge_limit:
                wf.add_jobs(merge_job)
                merge_job = None
                merge_count = 0
                merge_id += 1

        # do we need to finish the merge job?
        if merge_count > 0:
                wf.add_jobs(merge_job)
                # added by karan. need to reset the counters and
                # merge job
                merge_job = None
                merge_count = 0
                merge_id += 1

    # plan workflow
    wf.plan(
        dir=WORK_DIR / "runs",
        sites = ["condorpool"],
        output_sites=["remote"],
        verbose=1,
        submit=args.submit
    )

def parse_inputs():
    parser = ap.ArgumentParser(description='Workflow to run OSG two-photon simulations')

    parser.add_argument('-z', dest='element', required=True, help="Element")
    parser.add_argument('-a', dest='isotope', required=True, help="Isotope")
    parser.add_argument('-g1', dest='gamma1', required=True, help="First gamma-ray in decay")
    parser.add_argument('-g2', dest='gamma2', required=True, help="Second gamma-ray in decay")
    parser.add_argument('-e', dest='total_events', required=True, type=int, help="Total number of simulated events")
    parser.add_argument('-b', dest='batch_size', required=True, type=int, help="Events per simulation")
    parser.add_argument('--submit', dest='submit', required=True, help="Submit simulation")

    args, unknown = parser.parse_known_args()


    return args

def main():

    args = parse_inputs()
    create_workflow(args)


if __name__ == "__main__":
    main()