import React, { useState } from "react";
import Header from "../components/Header";
import Card from "../components/Card";
import Button from "../components/Button";
import StatusBadge from "../components/StatusBadge";
import { connectDoctor } from "../services/api";

interface Props {
  caseData: any;
  onBack: () => void;
}

const DiagnosisResult: React.FC<Props> = ({ caseData, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [doctorInfo, setDoctorInfo] = useState<any>(null);
  const [error, setError] = useState("");

  const handleConnectDoctor = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await connectDoctor(caseData.CaseID);
      setDoctorInfo(response);
    } catch (err) {
      setError("Unable to connect to doctor.");
    } finally {
      setLoading(false);
    }
  };

  const riskColorClass =
    caseData.RiskLevel === "EMERGENCY"
      ? "bg-emergency"
      : caseData.RiskLevel === "URGENT"
      ? "bg-urgent"
      : "bg-routine";

  return (
    <div className="min-h-screen bg-background">
      <Header
        title="Diagnosis Result"
        subtitle={caseData.CaseID}
        showBack
        onBack={onBack}
      />

      {/* Risk Banner */}
      <div className={`${riskColorClass} text-white py-3`}>
        <div className="max-w-md mx-auto px-4 flex justify-between items-center">
          <span className="text-sm font-semibold tracking-wide">
            {caseData.RiskLevel}
          </span>
        </div>
      </div>

      <div className="max-w-md mx-auto px-4 mt-6 space-y-5">

        {/* Diagnosis Details */}
        <Card>
          <div className="space-y-2">
            <p className="text-sm font-medium">
              {caseData.PrimaryDiagnosis}
            </p>

            <p className="text-xs text-textSecondary">
              ICD-10: {caseData.ICD10Code}
            </p>

            <p className="text-xs">
              Confidence: {caseData.ConfidencePercent}%
            </p>
          </div>
        </Card>

        {/* Risk Reason */}
        <Card>
          <p className="text-sm font-medium mb-2">
            Clinical Assessment
          </p>
          <p className="text-xs text-textSecondary">
            {caseData.RiskReason}
          </p>
        </Card>

        {/* Immediate Actions */}
        <Card>
          <p className="text-sm font-medium mb-2">
            Immediate Actions
          </p>
          <ul className="space-y-2">
            {caseData.ImmediateActions.map(
              (action: string, index: number) => (
                <li key={index} className="text-xs text-textPrimary">
                  {index + 1}. {action}
                </li>
              )
            )}
          </ul>
        </Card>

        {/* Connect Doctor */}
        {!doctorInfo && (
          <Button
            label={loading ? "Connecting..." : "Connect to Doctor"}
            variant={
              caseData.RiskLevel === "EMERGENCY"
                ? "emergency"
                : "primary"
            }
            onClick={handleConnectDoctor}
            disabled={loading}
          />
        )}

        {/* Doctor Assigned Info */}
        {doctorInfo && (
          <Card>
            <div className="space-y-2">
              <p className="text-sm font-medium">
                Assigned Doctor
              </p>
              <p className="text-xs">
                {doctorInfo.DoctorName}
              </p>
              <p className="text-xs text-textSecondary">
                {doctorInfo.Specialization}
              </p>
              <p className="text-xs text-textSecondary">
                Distance: {doctorInfo.DistanceKm} km
              </p>
            </div>
          </Card>
        )}

        {/* WhatsApp Preview */}
        {doctorInfo?.whatsapp_preview && (
          <Card>
            <p className="text-sm font-medium mb-2">
              Case Report Preview
            </p>
            <pre className="text-xs whitespace-pre-wrap text-textSecondary">
              {doctorInfo.whatsapp_preview}
            </pre>
          </Card>
        )}

        {error && (
          <div className="text-sm text-emergency">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default DiagnosisResult;