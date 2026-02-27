import React, { useState } from "react";
import Header from "../components/Header";
import Card from "../components/Card";
import Button from "../components/Button";
import { diagnoseCase } from "../services/api";

interface Props {
  asha: any;
  patientId: string;
  onBack: () => void;
  onDiagnosisComplete: (caseData: any) => void;
}

const Assessment: React.FC<Props> = ({
  asha,
  patientId,
  onBack,
  onDiagnosisComplete,
}) => {
  const [symptoms, setSymptoms] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    if (!symptoms.trim()) {
      setError("Please enter symptoms before analyzing.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const response = await diagnoseCase({
        PatientID: patientId,
        ASHAWorkerID: asha.ASHAWorkerID,
        SymptomsRaw: symptoms,
        Language: "en-IN",
      });

      onDiagnosisComplete(response);
    } catch (err) {
      setError("Diagnosis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header
        title="New Assessment"
        subtitle="Enter patient symptoms"
        showBack
        onBack={onBack}
      />

      <div className="max-w-md mx-auto px-4 mt-6">

        <Card>
          <div className="space-y-4">

            <div>
              <label className="block text-sm font-medium text-textPrimary mb-2">
                Symptoms
              </label>
              <textarea
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                rows={5}
                className="w-full border border-gray-300 px-3 py-2 text-sm focus:outline-none resize-none"
                placeholder="Describe symptoms observed..."
              />
            </div>

            {error && (
              <div className="text-sm text-emergency">
                {error}
              </div>
            )}

            <Button
              label={loading ? "Analyzing..." : "Analyze Symptoms"}
              variant="primary"
              onClick={handleAnalyze}
              disabled={loading}
            />

          </div>
        </Card>

      </div>
    </div>
  );
};

export default Assessment;