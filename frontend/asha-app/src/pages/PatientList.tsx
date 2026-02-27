import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import Card from "../components/Card";
import Button from "../components/Button";
import StatusBadge from "../components/StatusBadge";
import { getPatients } from "../services/api";

interface PatientListProps {
  asha: any;
  onSelectPatient: (id: string) => void;
  onAddPatient: () => void;
}

const PatientList: React.FC<PatientListProps> = ({
  asha,
  onSelectPatient,
  onAddPatient,
}) => {
  const [patients, setPatients] = useState<any[]>([]);
  const [filtered, setFiltered] = useState<any[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const data = await getPatients(asha.ASHAWorkerID);
      setPatients(data);
      setFiltered(data);
    } catch (error) {
      console.error("Error fetching patients", error);
    }
  };

  const handleSearch = (value: string) => {
    setSearch(value);
    const lower = value.toLowerCase();
    const filteredData = patients.filter(
      (p) =>
        p.Name.toLowerCase().includes(lower) ||
        p.Village.toLowerCase().includes(lower)
    );
    setFiltered(filteredData);
  };

  return (
    <div className="min-h-screen bg-background">
      <Header
        title="MediConnect"
        subtitle={`${asha.Name} | ${asha.Block} Block`}
      />

      <div className="max-w-md mx-auto px-4 mt-6">

        {/* Search */}
        <div className="mb-4">
          <input
            type="text"
            value={search}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search patient..."
            className="w-full border border-gray-300 px-3 py-2 text-sm focus:outline-none"
          />
        </div>

        {/* Patient List */}
        <div className="space-y-3">
          {filtered.map((patient) => (
            <Card
              key={patient.PatientID}
              onClick={() => onSelectPatient(patient.PatientID)}
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm font-medium text-textPrimary">
                    {patient.Name}, {patient.Age}
                    {patient.Gender}
                  </p>
                  <p className="text-xs text-textSecondary">
                    {patient.Village}
                  </p>
                </div>

                <StatusBadge status="ROUTINE" />
              </div>
            </Card>
          ))}
        </div>

        {/* Add Patient Button */}
        <div className="mt-6">
          <Button
            label="Add New Patient"
            variant="primary"
            onClick={onAddPatient}
          />
        </div>

      </div>
    </div>
  );
};

export default PatientList;