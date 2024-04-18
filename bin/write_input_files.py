#!/usr/bin/env python3
'''
Author:     Connor Natzke
Date:       Mar 2021
Revision:   Oct 2023
Purpose:    Generates input files for PEGASUS workflows
'''
import argparse
import shutil
from pathlib import Path

def prepare_directories(dir):
    dir = Path(dir)
    if not dir.is_dir():
        try:
            print(f'\nCreating: {dir}')
            dir.mkdir(parents=True)
        except OSError as error:
            print(error)


def write_multipole_file(args):
    file_contents = (
        f'{float(args.gamma2)} {float(args.gamma2)} 2 0 0\n'
        f'{float(args.gamma1) + float(args.gamma2)} {float(args.gamma1)} 2 0 0\n'
    )
    if args.decay_mode == "beta_minus":
        file_name = f"{args.data_dir}/z{int(args.element) + 1}.a{args.isotope}.multipole"
    elif args.decay_mode == "beta_plus":
        file_name = f"{args.data_dir}/z{int(args.element) - 1}.a{args.isotope}.multipole"
    else:
        print(f"Unknown decay mode: {args.decay_mode}")
        exit(1)

    file = open(file_name, "w")
    file.write(file_contents)
    file.close()


def write_decay_file(args):
    if args.decay_mode == "beta_minus":
        file_contents = (
        '#  Excitation  Halflife    Mode    Daughter    Ex  Intensity   Q\n'
        'P  0.000000    1.0000e+02\n'
        '   BetaMinus   0.0000  1.0000e+00\n'
        f"   BetaMinus   {float(args.gamma1) + float(args.gamma2)}    1.0000e+00  10.0\n"
        )
    elif args.decay_mode == "beta_plus":
        file_contents = (
        '#  Excitation  Halflife    Mode    Daughter    Ex  Intensity   Q\n'
        'P  0.000000    1.0000e+02\n'
        '   BetaPlus   0.0000  1.0000e+00\n'
        f"   BetaPlus   {float(args.gamma1) + float(args.gamma2)}    1.0000e+00  10.0\n"
        )
    else:
        print(f"Unknown decay mode: {args.decay_mode}")
        exit(1)

    file_name = f"{args.data_dir}/z{args.element}.a{args.isotope}.decay"
    file = open(file_name, "w")
    file.write(file_contents)
    file.close()


def write_evap_file(args):
    file_contents = (
        f'{float(args.gamma2)} {float(args.gamma2)} 100.0 2+ 1.0e-12 2.00 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n'
        f'{float(args.gamma2) + float(args.gamma1)} {float(args.gamma1)} 100.0 2+ 1.0e-12 2.00 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n'
    )
    if args.decay_mode == "beta_minus":
        file_name = f"{args.data_dir}/z{int(args.element) + 1}.a{args.isotope}.evap"
    elif args.decay_mode == "beta_plus":
        file_name = f"{args.data_dir}/z{int(args.element) - 1}.a{args.isotope}.evap"
    else:
        print(f"Unknown decay mode: {args.decay_mode}")
        exit(1)
    file = open(file_name, "w")
    file.write(file_contents)
    file.close()


def write_run_macro(args):
    '''Creates run macro_file
    '''
    if args.decay_mode == 'beta_minus':
        daughter_element = args.element + 1
    elif args.decay_mode == "beta_plus":
        daughter_element = args.element - 1
    else:
        print(f"Unknown decay mode: {args.decay_mode}")
        exit(1)

    for z_dist in [0, 2, 4]:
        if z_dist == 0:
            dist_line = "/grdm/setAngularCorrelationCoefficients 0 0 0"
        if z_dist == 2:
            dist_line = "/grdm/setAngularCorrelationCoefficients 1 0 0"
        if z_dist == 4:
            dist_line = "/grdm/setAngularCorrelationCoefficients 0 1 0"

        file_contents = (
            '#--- Physics List ----------------------------------------------------\n'
            '/DetSys/phys/SelectPhysics emlivermore\n\n'
            '/cuts/setLowEdge 250 eV\n\n'
            '/run/initialize\n'
            '/process/em/fluo true\n'
            '/process/em/auger true\n'
            '/process/em/pixe true\n\n'
            '#--- Detector Properties ---------------------------------------------\n'
            '/DetSys/det/SetCustomRadialDistance 14.5 cm\n'
            '/DetSys/det/SetCustomShieldsPresent 0\n'
            '/DetSys/det/SetCustomExtensionSuppressorLocation 0\n\n'
            '/DetSys/det/SetCustomDeadLayer 1 1 0\n'
            '/DetSys/det/addGriffinCustomDetector 1\n'
            '/DetSys/det/SetCustomDeadLayer 2 2 0\n'
            '/DetSys/det/addGriffinCustomDetector 2\n'
            '/DetSys/det/SetCustomDeadLayer 3 3 0\n'
            '/DetSys/det/addGriffinCustomDetector 3\n'
            '/DetSys/det/SetCustomDeadLayer 4 4 0\n'
            '/DetSys/det/addGriffinCustomDetector 4\n'
            '/DetSys/det/SetCustomDeadLayer 5 5 0\n'
            '/DetSys/det/addGriffinCustomDetector 5\n'
            '/DetSys/det/SetCustomDeadLayer 6 6 0\n'
            '/DetSys/det/addGriffinCustomDetector 6\n'
            '/DetSys/det/SetCustomDeadLayer 7 7 0\n'
            '/DetSys/det/addGriffinCustomDetector 7\n'
            '/DetSys/det/SetCustomDeadLayer 8 8 0\n'
            '/DetSys/det/addGriffinCustomDetector 8\n'
            '/DetSys/det/SetCustomDeadLayer 9 9 0\n'
            '/DetSys/det/addGriffinCustomDetector 9\n'
            '/DetSys/det/SetCustomDeadLayer 10 10 0\n'
            '/DetSys/det/addGriffinCustomDetector 10\n'
            '/DetSys/det/SetCustomDeadLayer 11 11 0\n'
            '/DetSys/det/addGriffinCustomDetector 11\n'
            '/DetSys/det/SetCustomDeadLayer 12 12 0\n'
            '/DetSys/det/addGriffinCustomDetector 12\n'
            '/DetSys/det/SetCustomDeadLayer 13 13 0\n'
            '/DetSys/det/addGriffinCustomDetector 13\n'
            '/DetSys/det/SetCustomDeadLayer 14 14 0\n'
            '/DetSys/det/addGriffinCustomDetector 14\n'
            '/DetSys/det/SetCustomDeadLayer 15 15 0\n'
            '/DetSys/det/addGriffinCustomDetector 15\n'
            '/DetSys/det/SetCustomDeadLayer 16 16 0\n'
            '/DetSys/det/addGriffinCustomDetector 16\n'
            '#--- Auxiliary Properties --------------------------------------------\n'
            '/DetSys/app/addGriffinStructure 0\n\n'
            '#--- Verbosity Properties --------------------------------------------\n'
            '/control/verbose 1\n'
            '/run/verbose 0\n'
            '/event/verbose 0\n'
            '/tracking/verbose 0\n\n'
            '#--- User Defined Decays ----------------------------------------------\n'
            '# parent\n'
            f"/grdm/setRadioactiveDecayFile {args.element} {args.isotope} z{args.element}.a{args.isotope}.decay\n"
            '# daughter\n'
            f"/grdm/setPhotoEvaporationFile {daughter_element} {args.isotope} z{daughter_element}.a{args.isotope}.evap\n"
            f"/grdm/setMultipoleFile {daughter_element} {args.isotope} z{daughter_element}.a{args.isotope}.multipole\n"
            f"/grdm/setMultipoleGroundStateSpinAngularMomentum {daughter_element} {args.isotope} 0.0\n"
            f'{dist_line}\n\n'
            '#--- Beam Properties -------------------------------------------------\n'
            '/gun/particle ion\n'
            f"/gun/ion {args.element} {args.isotope}\n"
            f"/grdm/nucleusLimits {args.isotope} {args.isotope} {args.element} {args.element}\n\n"
            f"/run/beamOn {args.batch_events}\n"
        )
        file_name = f"{args.data_dir}/run_macro.z{z_dist}.mac"
        file = open(file_name, 'w')
        file.write(file_contents)
        file.close()

        
def copy_settings_file(args):
        setting_file_source = f"{Path.cwd()}/inputs/Settings.dat"
        shutil.copy(setting_file_source, args.data_dir)

def copy_calibration_file(args):
        calibration_file_source = f"{Path.cwd()}/inputs/calibration_mapping.cal"
        shutil.copy(calibration_file_source, args.data_dir)

def copy_helpers(args):
        helper_file_source = f"{Path.cwd()}/inputs/helpers/AngularCorrelationHelper.cxx"
        helper_header_source = f"{Path.cwd()}/inputs/helpers/AngularCorrelationHelper.hh"
        shutil.copy(helper_file_source, args.data_dir)
        shutil.copy(helper_header_source, args.data_dir)

def copy_processing_codes(args):
        file_source = f"{Path.cwd()}/inputs/processing-code/processSimulationOutputOSG.C"
        shutil.copy(file_source, args.data_dir)

def main(args):

    prepare_directories(args.data_dir)
    # Create input files
    write_multipole_file(args)
    write_decay_file(args)
    write_evap_file(args)
    write_run_macro(args)
    # copy_settings_file(args)
    copy_calibration_file(args)
    copy_helpers(args)
    copy_processing_codes(args)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Script to prepare files for OSG GGAC simulations')

    parser.add_argument('-z', dest='element', required=True,
                        help="Element (atomic) number", type=int)
    parser.add_argument('-a', dest='isotope', required=True,
                        help="Isotope number", type=int)
    parser.add_argument('--decay-mode', dest='decay_mode', required=True,
                        help="Decay mode [beta_plus, beta_minus]")
    parser.add_argument('-g1', dest='gamma1', required=True,
                        help="First gamma energy in cascade [keV]", type=int)
    parser.add_argument('-g2', dest='gamma2', required=True,
                        help="Second gamma energy in cascade [keV]", type=int)
    parser.add_argument('-r', dest='radius', required=True,
                        help="HPGe radius [mm]", type=int)
    parser.add_argument('--data-dir', dest='data_dir', required=True,
                        help="Directory for output data file")
    parser.add_argument('--batch-events', dest='batch_events', required=True,
                        help="Number of primary events", type=int)

    args, unknown = parser.parse_known_args()

    main(args)
