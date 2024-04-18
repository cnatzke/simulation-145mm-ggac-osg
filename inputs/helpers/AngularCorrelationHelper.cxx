#include "AngularCorrelationHelper.hh"

double ggHigh = 400.; // max. absolute time difference gamma-gamma
int gammaEnergyHigh = 8000;
int gammaEnergyLow = 10;
int gammaBinSize = 1;
int nBinsGamma = (gammaEnergyHigh - gammaEnergyLow) / gammaBinSize;

void AngularCorrelationHelper::CreateHistograms(unsigned int slot)
{
   // for each angle (and the sum) we want
   // for single crystal and addback
   // with and without coincident betas
   // coincident and time-random gamma-gamma
   for (int i = 0; i < static_cast<int>(fAngleCombinations.size()); ++i)
   {
      fH2[slot][Form("gammaGamma%d", i)] =
          new TH2D(Form("gammaGamma%d", i), Form("%.1f^{o}: #gamma-#gamma, |#Deltat_{#gamma-#gamma}| < %.1f", fAngleCombinations[i].first, ggHigh), nGammaBins, gammaEnergyLow, gammaEnergyHigh, nGammaBins, gammaEnergyLow, gammaEnergyHigh);
   }
   fH2[slot]["gammaGamma"] = new TH2D("gammaGamma", Form("#gamma-#gamma, |#Deltat_{#gamma-#gamma}| < %.1f", ggHigh), nGammaBins, gammaEnergyLow, gammaEnergyHigh, nGammaBins, gammaEnergyLow, gammaEnergyHigh);
   // plus hitpatterns for gamma-gamma and beta-gamma for single crystals
   fH2[slot]["gammaGammaHP"] = new TH2D("gammaGammaHP", "#gamma-#gamma hit pattern", 65, 0., 65., 65, 0., 65.);

   // additionally 1D spectra of gammas
   // for single crystal and addback
   // with and without coincident betas
   fH1[slot]["gammaEnergy"] = new TH1D("gammaEnergy", "#gamma Singles", nGammaBins, gammaEnergyLow, gammaEnergyHigh);

   // and timing spectra for gamma-gamma and beta-gamma
   fH1[slot]["gammaGammaTiming"] = new TH1D("gammaGammaTiming", "#Deltat_{#gamma-#gamma}", 500, 0., 500.);
}

void AngularCorrelationHelper::Exec(unsigned int slot, TGriffin &grif)
{
   // without addback
   for (auto g1 = 0; g1 < grif.GetMultiplicity(); ++g1)
   {
      auto grif1 = grif.GetGriffinHit(g1);
      fH1[slot].at("gammaEnergy")->Fill(grif1->GetEnergy());
      for (auto g2 = 0; g2 < grif.GetMultiplicity(); ++g2)
      {
         if (g1 == g2)
            continue;
         auto grif2 = grif.GetGriffinHit(g2);
         double angle = grif1->GetPosition(145.).Angle(grif2->GetPosition(145.)) * 180. / TMath::Pi();
         if (angle < 0.0001)
            continue;
         auto angleIndex = fAngleMap.lower_bound(angle - 0.0005);
         double ggTime = TMath::Abs(grif1->GetTime() - grif2->GetTime());
         fH1[slot].at("gammaGammaTiming")->Fill(ggTime);
         fH2[slot].at("gammaGammaHP")->Fill(grif1->GetArrayNumber(), grif2->GetArrayNumber());

         if (ggTime < ggHigh)
         {
            fH2[slot].at("gammaGamma")->Fill(grif1->GetEnergy(), grif2->GetEnergy());
            fH2[slot].at(Form("gammaGamma%d", angleIndex->second))->Fill(grif1->GetEnergy(), grif2->GetEnergy());
         }
      }
   }
}
