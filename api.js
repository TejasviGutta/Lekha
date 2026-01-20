const BASE_URL = "http://10.0.2.2:8000";

export async function correctWord(word) {
  const res = await fetch(`${BASE_URL}/correct`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ word }),
  });

  if (!res.ok) {
    throw new Error("Backend error");
  }

  return await res.json();
}

export async function confirmCorrection(original, corrected) {
  const res = await fetch(`${BASE_URL}/confirm`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ original, corrected }),
  });

  return await res.json();
}
