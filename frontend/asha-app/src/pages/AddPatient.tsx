import React, { useState } from "react";
import Header from "../components/Header";
import Card from "../components/Card";
import Button from "../components/Button";
import { createPatient } from "../services/api";

interface Props {
  asha: any;
  onBack: () => void;
  onSuccess: (patientId: string) => void;
}

const AddPatient: React.FC<Props> = ({
  asha,
  onBack,
  onSuccess,
}) => {
  const [form, setForm] = useState({
    Name: "",
    Age: "",
    Gender: "",
    Village: "",
    KnownConditions: "",
    KnownAllergies: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (key: string, value: string) => {
    setForm({ ...form, [key]: value });
  };

  const handleSubmit = async () => {
    if (!form.Name || !form.Age || !form.Gender || !form.Village) {
      setError("Please fill all required fields.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const payload = {
        ...form,
        Age: parseInt(form.Age),
        ASHAWorkerID: asha.ASHAWorkerID,
        KnownConditions: form.KnownConditions
          ? form.KnownConditions.split(",").map((c) => c.trim())
          : [],
        KnownAllergies: form.KnownAllergies
          ? form.KnownAllergies.split(",").map((a) => a.trim())
          : [],
      };

      const response = await createPatient(payload);
      onSuccess(response.PatientID);
    } catch (err) {
      setError("Failed to create patient.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header
        title="Add Patient"
        subtitle="Enter patient details"
        showBack
        onBack={onBack}
      />

      <div className="max-w-md mx-auto px-4 mt-6">
        <Card>
          <div className="space-y-4">

            <Input label="Full Name" value={form.Name} onChange={(v) => handleChange("Name", v)} />
            <Input label="Age" value={form.Age} onChange={(v) => handleChange("Age", v)} />
            <Input label="Gender" value={form.Gender} onChange={(v) => handleChange("Gender", v)} />
            <Input label="Village" value={form.Village} onChange={(v) => handleChange("Village", v)} />
            <Input label="Known Conditions (comma separated)" value={form.KnownConditions} onChange={(v) => handleChange("KnownConditions", v)} />
            <Input label="Known Allergies (comma separated)" value={form.KnownAllergies} onChange={(v) => handleChange("KnownAllergies", v)} />

            {error && (
              <div className="text-sm text-emergency">
                {error}
              </div>
            )}

            <Button
              label={loading ? "Saving..." : "Save Patient"}
              variant="primary"
              onClick={handleSubmit}
              disabled={loading}
            />

          </div>
        </Card>
      </div>
    </div>
  );
};

const Input = ({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) => (
  <div>
    <label className="block text-sm font-medium mb-1 text-textPrimary">
      {label}
    </label>
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full border border-gray-300 px-3 py-2 text-sm focus:outline-none"
    />
  </div>
);

export default AddPatient;