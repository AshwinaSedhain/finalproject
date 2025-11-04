// File: frontend/src/pages/DashboardPage.jsx

import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "../context/AuthContext";
import { sendChatMessage } from "../api";
import Navbar from "../components/NavBar";
import Sidebar from "../components/SideBar";
import DatabaseSetupModal from "../components/DatabaseSetupModal";
const Canvas = React.lazy(() => import('../components/Canvas')); // Lazy load for performance
import ChatInput from "../components/ChatInput";
import ChatMessage from "../components/ChatMessage";

const DashboardPage = () => {
  const { token } = useAuth();
  const messagesEndRef = useRef(null);

  const [conversations, setConversations] = useState({});
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // This state is critical for showing the DB setup modal
  const [dbConfig, setDbConfig] = useState(() => {
    try {
      // Safely parse the config from local storage
      return JSON.parse(localStorage.getItem("dbConfig"));
    } catch {
      return null;
    }
  });

  const [sidebarOpen, setSidebarOpen] = useState(() => typeof window !== "undefined" ? window.innerWidth >= 1024 : false);

  // --- THIS IS THE CRITICAL FUNCTION TO SAVE THE DB CONFIG ---
  const handleSaveDbConfig = (config) => {
    // Save the config to local storage so the user doesn't have to enter it again
    localStorage.setItem("dbConfig", JSON.stringify(config));
    // Update the component's state to remove the modal and show the dashboard
    setDbConfig(config);
  };

  // --- All your other functions like handleSendMessage, etc. remain the same ---
  const handleSendMessage = async (prompt) => {
    if (!prompt.trim() || isLoading || !dbConfig) return;
    let convoId = activeConversationId || Date.now().toString();
    if (!activeConversationId) {
        setActiveConversationId(convoId);
        const newConversation = {
            id: convoId, title: prompt, timestamp: new Date().toISOString(),
            messages: [{ role: "assistant", content: 'Okay, starting a new analysis...' }], reports: [],
        };
        setConversations(prev => ({ ...prev, [convoId]: newConversation }));
    }
    const userMessage = { role: "user", content: prompt };
    setConversations(prev => ({ ...prev, [convoId]: { ...prev[convoId], messages: [...prev[convoId].messages, userMessage] } }));
    setIsLoading(true);
    try {
        const aiResult = await sendChatMessage(prompt, token);
        let chartData = null;
        if (aiResult?.visualization) {
            try { chartData = JSON.parse(aiResult.visualization); }
            catch (e) { console.error("Failed to parse visualization JSON"); }
        }
        const newReportId = chartData ? Date.now().toString() : null;
        const aiMessage = { role: "assistant", content: aiResult.response, reportId: newReportId };
        const newReport = chartData ? { id: newReportId, title: prompt, type: 'chart', chartData } : null;
        setConversations(prev => ({ ...prev, [convoId]: { ...prev[convoId], messages: [...prev[convoId].messages, aiMessage], reports: newReport ? [...prev[convoId].reports, newReport] : prev[convoId].reports } }));
    } catch (error) {
        const errorMessage = { role: "assistant", content: `Sorry, an error occurred: ${error.message}` };
        setConversations(prev => ({ ...prev, [convoId]: { ...prev[convoId], messages: [...prev[convoId].messages, errorMessage] } }));
    } finally {
        setIsLoading(false);
    }
  };
  const handleActivityClick = (activity) => { setActiveConversationId(activity.id); setSidebarOpen(false); };
  const handleNewChat = () => { setActiveConversationId(null); setSidebarOpen(false); };
  
  const currentConversation = conversations[activeConversationId];
  const messages = currentConversation?.messages || [];
  const openReports = currentConversation?.reports || [];
  const activities = Object.values(conversations).map(convo => ({
    id: convo.id,
    title: convo.title,
    timestamp: convo.timestamp,
  })).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  const activeReportId = openReports.length > 0 ? openReports[openReports.length - 1].id : null;
  const currentReport = openReports.find((r) => r.id === activeReportId);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // --- THIS IS THE CRITICAL LOGIC TO SHOW THE MODAL ---
  // If there is no database configuration, render the setup modal.
  if (!dbConfig) {
    return <DatabaseSetupModal isOpen={true} onSave={handleSaveDbConfig} />;
  }

  // --- This is the main dashboard, which will ONLY render if dbConfig exists ---
  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Navbar onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        activities={activities}
        onActivityClick={handleActivityClick}
        activeActivityId={activeConversationId}
        showCloseButton={true}
        onNewChat={handleNewChat}
      />
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, i) => (<ChatMessage key={i} message={msg} />))}
            {isLoading && <ChatMessage message={{ role: 'assistant' }} isLoading={true} />}
            <div ref={messagesEndRef} />
          </div>
          <ChatInput onSend={handleSendMessage} disabled={!dbConfig || isLoading} />
        </div>
        {openReports.length > 0 && (
          <React.Suspense fallback={<div className="w-1/2 flex items-center justify-center"><p>Loading chart...</p></div>}>
              <Canvas
                report={currentReport}
                allReports={openReports}
                activeReportId={activeReportId}
                onReportChange={(id) => { /* Placeholder */ }}
              />
          </React.Suspense>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;