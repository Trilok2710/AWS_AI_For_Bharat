import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import Card from "../components/Card";
import Button from "../components/Button";
import StatusBadge from "../components/StatusBadge";
import {
  getPatientProfile,
  getPatientCases,
} from "../services/api";

interface Props {
  patientId: string;
  onBack: () => void;
  onStartAssessment: () => void;
}

const PatientProfile: React.FC<Props> = ({
  patientId,
  onBack,
  onStartAssessment,
}) => {
  const [patient, setPatient] = useState<any>(null);
  const [cases, setCases] = useState<any[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const profile = await getPatientProfile(patientId);
      const history = await getPatientCases(patientId);
      setPatient(profile);
      setCases(history);
    } catch (err) {
      console.error(err);
    }
  };

  if (!patient) return null;

  return (
    <div className="min-h-screen bg-background">
      <Header
        title={patient.Name}
        subtitle={`${patient.Age} | ${patient.Gender} | ${patient.Village}`}
        showBack
        onBack={onBack}
      />

      <div className="max-w-md mx-auto px-4 mt-6 space-y-5">

        {/* Known Conditions */}
        <Card>
          <p className="text-sm font-medium mb-2">Known Conditions</p>
          {patient.KnownConditions?.length === 0 ? (
            <p className="text-xs text-textSecondary">
              No known conditions recorded.
            </p>
          ) : (
            <ul className="space-y-1">
              {patient.KnownConditions.map((condition: string, index: number) => (
                <li key={index} className="text-xs text-textPrimary">
                  {condition}
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* Case History */}
        <div>
          <p className="text-sm font-medium mb-2">Case History</p>

          <div className="space-y-3">
            {cases.map((c) => (
              <Card key={c.CaseID}>
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm font-medium">
                      {c.PrimaryDiagnosis}
                    </p>
                    <p className="text-xs text-textSecondary">
                      {c.ICD10Code}
                    </p>
                  </div>
                  <StatusBadge status={c.RiskLevel} />
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Start Assessment */}
        <Button
  label="Start New Assessment"
  variant="primary"
  onClick={onStartAssessment}
/>

      </div>
    </div>
  );
};

export default PatientProfile;