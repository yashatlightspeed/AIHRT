import { useState } from "react";
import InterviewRoom from "./components/InterviewRoom";
import RecruiterDashboard from "./components/RecruiterDashboard";
import CandidateSetup from "./components/CandidateSetup";
import Landing from "./pages/Landing";
import "./index.css";

export default function App() {
  const [page, setPage] = useState("landing"); // landing | setup | interview | dashboard
  const [session, setSession] = useState(null); // { interviewId, sessionId, candidateId, candidateName }

  const handleInterviewComplete = (interviewId) => {
    setSession((s) => ({ ...s, interviewId }));
    setPage("dashboard");
  };

  return (
    <div className="app-root">
      {page === "landing" && (
        <Landing
          onStartCandidate={() => setPage("setup")}
          onOpenDashboard={() => setPage("dashboard")}
        />
      )}
      {page === "setup" && (
        <CandidateSetup
          onReady={(sessionData) => {
            setSession(sessionData);
            setPage("interview");
          }}
        />
      )}
      {page === "interview" && session && (
        <InterviewRoom
          session={session}
          onComplete={handleInterviewComplete}
        />
      )}
      {page === "dashboard" && (
        <RecruiterDashboard
          interviewId={session?.interviewId}
          onBack={() => setPage("landing")}
        />
      )}
    </div>
  );
}
