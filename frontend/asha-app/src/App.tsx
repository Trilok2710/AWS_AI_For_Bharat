import React, { useState } from "react";
import Login from "./pages/Login";
import PatientList from "./pages/PatientList";
import PatientProfile from "./pages/PatientProfile";
import Assessment from "./pages/Assessment";
import DiagnosisResult from "./pages/DiagnosisResult";
import AddPatient from "./pages/AddPatient";

function App() {
  const [asha, setAsha] = useState<any>(null);
  const [selectedPatient, setSelectedPatient] = useState<string | null>(null);
  const [currentCase, setCurrentCase] = useState<any>(null);
  const [screen, setScreen] = useState<
    "profile" | "assessment" | "result" | "add"
  >("profile");

  if (!asha) {
    return <Login onLoginSuccess={setAsha} />;
  }

  if (screen === "add") {
    return (
      <AddPatient
        asha={asha}
        onBack={() => setScreen("profile")}
        onSuccess={(newPatientId) => {
          setSelectedPatient(newPatientId);
          setScreen("profile");
        }}
      />
    );
  }

  if (!selectedPatient) {
    return (
      <PatientList
        asha={asha}
        onSelectPatient={(id) => {
          setSelectedPatient(id);
          setScreen("profile");
        }}
        onAddPatient={() => setScreen("add")}
      />
    );
  }

  if (screen === "assessment") {
    return (
      <Assessment
        asha={asha}
        patientId={selectedPatient}
        onBack={() => setScreen("profile")}
        onDiagnosisComplete={(caseData) => {
          setCurrentCase(caseData);
          setScreen("result");
        }}
      />
    );
  }

  if (screen === "result" && currentCase) {
    return (
      <DiagnosisResult
        caseData={currentCase}
        onBack={() => setScreen("profile")}
      />
    );
  }

  return (
    <PatientProfile
      patientId={selectedPatient}
      onBack={() => {
        setSelectedPatient(null);
        setScreen("profile");
      }}
      onStartAssessment={() => setScreen("assessment")}
    />
  );
}

export default App;