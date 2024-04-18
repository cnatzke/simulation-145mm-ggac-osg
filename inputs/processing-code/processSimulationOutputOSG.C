// Author: C. Natzke
// Updated: Dec 2023

// --- USAGE:
// grsisort -l -b -q "processSimulationOutputOSG.C(gateCentroid,peakCentroid)"

#include <TSystem.h>
#include <TString.h>
#include <TObjArray.h>
#include <vector>

void fitSimulationOutput(Int_t gateCentroid, Int_t peakCentroid, TString inputFile, TString fitFile)
{

    Int_t verbosity = 1;
    // TString graphicsFileName = Form("%s/z-distributions/z_distributions.z%i.a%i.%i_%i.fitted.root", outputDir.Data(), element, isotope, gateCentroid, peakCentroid);
    // We exclude one angular index b/c it is two events in one crystal
    Int_t numIndices = 51;

    Int_t gate_low = gateCentroid - 2;
    Int_t gate_high = gateCentroid + 2;
    Int_t peak_low = peakCentroid - 2;
    Int_t peak_high = peakCentroid + 2;

    Float_t binCounts[numIndices];
    Float_t binCountsError[numIndices];
    Float_t indexValue[numIndices];
    // TFile *graphicsFile = new TFile(graphicsFileName.Data(), "recreate");
    // TH1D *total = NULL;
    std::ofstream fit_file(fitFile.Data());

    // --- basic logging
    std::cout << "Processing simulation output for cascade: " << gateCentroid << "-" << peakCentroid << std::endl;

    // This line is very important, if you remove it the final datafile won't
    // have the correct number of lines. Maybe due to initializing the file?
    fit_file << "index,counts,counts_error" << std::endl;

    TFile *f = new TFile(inputFile.Data(), "READ");

    if (!f || f->IsZombie())
    {
        std::cerr << "Error opening input file" << endl;
        exit(-1);
    }

    f->cd();

    for (int myIndex = 0; myIndex < numIndices; myIndex++)
    {
        if (verbosity > 0)
        {
            std::cout << "Processing index " << myIndex + 1 << " of " << numIndices << std::endl;
        }

        TString matrixName = Form("gammaGamma%i", myIndex);
        TH2D *matrix = static_cast<TH2D *>(f->Get(matrixName.Data()));

        // --- check for 0 entries
        if (matrix->GetEntries() < 100)
        {
            std::cerr << "Low/No counts in matrix for index: " << myIndex << std::endl;
            continue;
        }

        // --- project out coincident energy spectrum
        TH1D *projection = static_cast<TH1D *>(matrix->ProjectionY("projection", gateCentroid - 1, gateCentroid + 1));
        // projection->SetName(Form("projection_z%i_%i", 2 * k, myIndex));
        // projection->Sumw2();

        // --- check for 0 entries
        if (projection->GetEntries() < 10)
        {
            std::cerr << "Low/No counts in index " << myIndex << std::endl;
            continue;
        }

        // --- get counts in peak
        indexValue[myIndex] = myIndex;
        binCounts[myIndex] = projection->Integral(peakCentroid - 1, peakCentroid + 1);
        binCountsError[myIndex] = sqrt(binCounts[myIndex]);

        // --- Write values to file
        fit_file << myIndex << ",";
        fit_file << binCounts[myIndex] << ",";
        fit_file << binCountsError[myIndex] << "\n";

        // --- add index values to total histogram
        // if (j+ myIndex == 0)
        // {
        //     total = static_cast<TH1D *>(projection->Clone());
        //     // --- disconnect histogram from any input file
        //     total->SetDirectory(0);
        // }
        // else
        // {
        //     total->Add(projection, 1.0);
        // }
        // graphicsFile->cd();
        // projection->Write();

        delete projection;
        delete matrix;
    }

    // // --- create plot of index sensitive values
    // TGraphErrors *ge = new TGraphErrors(numIndices, indexValue, binCounts, 0, binCountsError);
    // ge->SetMarkerStyle(8);
    // ge->SetMarkerSize(0.6);
    // ge->SetName(Form("unweighted_distribution_z%d_%d", 2 * k, j));
    // ge->Write();

    f->Close();
    delete f;

    fit_file.close();
    std::cout << "\nFit data written to: " << fitFile.Data() << std::endl;
    // graphicsFile->cd();
    // if (total)
    // {
    //     total->SetName("totalProjection");
    //     total->Write();
    // }
    // graphicsFile->Close();
    // std::cout << "Fit graphics written to: " << graphicsFileName.Data() << std::endl;
}

void processSimulationOutputOSG(Int_t gateCentroid, Int_t peakCentroid)
{
    // Int_t gateCentroid = 602; // keV
    // Int_t peakCentroid = 158; // keV
    // Int_t element = 57;
    // Int_t isotope = 148;
    TString inputFileName = "AngularCorrelation00000-00000.root";
    TString fitFileName = "peak_areas.csv";

    fitSimulationOutput(gateCentroid, peakCentroid, inputFileName, fitFileName);

    // gApplication->Terminate();
}