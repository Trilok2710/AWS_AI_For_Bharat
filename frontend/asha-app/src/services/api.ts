const BASE_URL = "http://127.0.0.1:8000";

export async function login(phone: string, pin: string) {
  const response = await fetch(`${BASE_URL}/asha/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ phone, pin }),
  });

  if (!response.ok) {
    throw new Error("Login failed");
  }

  return response.json();
}

export async function getPatients(ashaId: string) {
  const response = await fetch(`${BASE_URL}/patients/${ashaId}`);

  if (!response.ok) {
    throw new Error("Failed to fetch patients");
  }

  return response.json();
}

export async function getPatientProfile(patientId: string) {
  const response = await fetch(`${BASE_URL}/patients/profile/${patientId}`);
  if (!response.ok) throw new Error("Failed to fetch profile");
  return response.json();
}

export async function getPatientCases(patientId: string) {
  const response = await fetch(`${BASE_URL}/cases/patient/${patientId}`);
  if (!response.ok) throw new Error("Failed to fetch cases");
  return response.json();
}

export async function diagnoseCase(payload: any) {
  const response = await fetch(`${BASE_URL}/cases/diagnose`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Diagnosis failed");
  }

  return response.json();
}

export async function connectDoctor(caseId: string) {
  const response = await fetch(`${BASE_URL}/cases/${caseId}/connect-doctor`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Doctor connection failed");
  }

  return response.json();
}

export async function createPatient(payload: any) {
  const response = await fetch(`${BASE_URL}/patients/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to create patient");
  }

  return response.json();
}