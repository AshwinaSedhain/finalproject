// File: frontend/src/pages/DashboardPage.jsx

import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "../context/AuthContext";
import { sendChatMessage } from "../api";
import Navbar from "../components/NavBar";
import Sidebar from "../components/SideBar";
import DatabaseSetupModal from "../components/DatabaseSetupModal";
const Canvas = React.lazy(() => import('../components/Canvas'));
import ChatInput from "../components/ChatInput";
import ChatMessage from "../components/ChatMessage";

const DashboardPage = () => {
  const { token } = useAuth();
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);
  
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(() => typeof window !== "undefined" ? window.innerWidth >= 1024 : false);
  
  const [dbConfig, setDbConfig] = useState(() => {
    try {
      const saved = localStorage.getItem("dbConfig");
      return saved ? JSON.parse(saved) : null;
    } catch { return null; }
  });

  const [conversations, setConversations] = useState(() => {
    try {
      const saved = localStorage.getItem("chatConversations");
      return saved ? JSON.parse(saved) : {};
    } catch { return {}; }
  });

  const [activeConversationId, setActiveConversationId] = useState(() => localStorage.getItem("activeChatId") || null);

  useEffect(() => {
    localStorage.setItem("chatConversations", JSON.stringify(conversations));
  }, [conversations]);

  useEffect(() => {
    if (activeConversationId) {
      localStorage.setItem("activeChatId", activeConversationId);
    } else {
      localStorage.removeItem("activeChatId");
    }
  }, [activeConversationId]);

  useEffect(() => {
    if (dbConfig && Object.keys(conversations).length === 0) {
      const initialConvoId = 'welcome-chat';
      const welcomeMessage = {
        id: initialConvoId, title: 'Welcome!', timestamp: new Date().toISOString(),
        messages: [{
          role: 'assistant',
          content: 'Hello! How can I assist you with your data today?' 
        }],
        reports: []
      };
      setConversations({ [initialConvoId]: welcomeMessage });
      setActiveConversationId(initialConvoId);
    }
  }, [dbConfig]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversations, isLoading]);

  const currentConversation = conversations[activeConversationId];
  const messages = currentConversation?.messages || [];
  const openReports = currentConversation?.reports || [];
  const chatHistory = Object.values(conversations).map(c => ({ id: c.id, title: c.title, timestamp: c.timestamp })).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  const activeReportId = openReports.length > 0 ? openReports[openReports.length - 1].id : null;
  const currentReport = openReports.find((r) => r.id === activeReportId);

  const handleSaveDbConfig = (config) => {
    if (config && config.connectionString) {
      localStorage.setItem("dbConfig", JSON.stringify(config));
      setDbConfig(config);
    }
  };
  
  const handleSendMessage = async (prompt) => {
    if (!prompt.trim() || isLoading || !dbConfig?.connectionString) return;
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;
    let convoId = activeConversationId;
    let isNewChat = false;
    if (!convoId || convoId === 'welcome-chat') {
        convoId = Date.now().toString();
        isNewChat = true;
    }
    if (isNewChat) {
        const newConvo = { id: convoId, title: prompt, timestamp: new Date().toISOString(), messages: [], reports: [] };
        setConversations(prev => ({ ...prev, [convoId]: newConvo }));
        setActiveConversationId(convoId);
    }
    const userMessage = { role: "user", content: prompt };
    setConversations(prev => ({ ...prev, [convoId]: { ...prev[convoId], messages: [...(prev[convoId]?.messages || []), userMessage] } }));
    setIsLoading(true);
    try {
      const aiResult = await sendChatMessage(prompt, token, signal);
      if (aiResult.cancelled) { setIsLoading(false); return; }
      let chartData = null;
      if (aiResult.visualization) { try { chartData = JSON.parse(aiResult.visualization); } catch (e) { console.error("Failed to parse viz JSON", e); } }
      const newReportId = chartData ? Date.now().toString() : null;
      const aiMessage = { role: "assistant", content: aiResult.response, reportId: newReportId };
      const newReport = chartData ? { id: newReportId, title: prompt, type: aiResult.chart_type || 'chart', chartData } : null;
      setConversations(prev => {
        const convo = prev[convoId];
        return { ...prev, [convoId]: { ...convo, messages: [...convo.messages, aiMessage], reports: newReport ? [...convo.reports, newReport] : convo.reports }};
      });
    } catch (error) {
      if (error.name !== 'AbortError') {
        const errorMessage = { role: "assistant", content: `Sorry, an error occurred: ${error.message}` };
        setConversations(prev => ({ ...prev, [convoId]: { ...prev[convoId], messages: [...prev[convoId].messages, errorMessage] } }));
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleStop = () => { if (abortControllerRef.current) { abortControllerRef.current.abort(); } };
  const handleSelectChat = (chat) => { setActiveConversationId(chat.id); setSidebarOpen(false); };
  const handleNewChat = () => {
    const newId = Date.now().toString();
    const newConvo = { id: newId, title: "New Conversation", timestamp: new Date().toISOString(), messages: [{ role: 'assistant', content: 'Ready for your next question!' }], reports: [] };
    setConversations(prev => ({ ...prev, [newId]: newConvo }));
    setActiveConversationId(newId);
    setSidebarOpen(false);
  };
  const handleDeleteChat = (chatIdToDelete) => {
    setConversations(prev => {
      const newConversations = { ...prev };
      delete newConversations[chatIdToDelete];
      return newConversations;
    });
    if (activeConversationId === chatIdToDelete) {
      const remainingChatIds = Object.keys(conversations).filter(id => id !== chatIdToDelete);
      if (remainingChatIds.length > 0) {
        const mostRecentChatId = remainingChatIds.sort((a, b) => new Date(conversations[b].timestamp) - new Date(conversations[a].timestamp))[0];
        setActiveConversationId(mostRecentChatId);
      } else { setActiveConversationId(null); }
    }
  };

  if (!dbConfig || !dbConfig.connectionString) {
    return ( <DatabaseSetupModal isOpen={true} onSave={handleSaveDbConfig} /> );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Navbar onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)}
          chatHistory={chatHistory} onSelectChat={handleSelectChat}
          activeChatId={activeConversationId} onNewChat={handleNewChat}
          onDeleteChat={handleDeleteChat} showCloseButton={true}
        />
        <div className={`flex-1 flex flex-col`}>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, i) => (<ChatMessage key={i} message={msg} />))}
            {isLoading && <ChatMessage message={{ role: 'assistant' }} isLoading={true} />}
            <div ref={messagesEndRef} />
          </div>
          <ChatInput onSend={handleSendMessage} disabled={!dbConfig} isLoading={isLoading} onStop={handleStop} />
        </div>
        {openReports.length > 0 && (
          <React.Suspense fallback={<div className="w-1/2 p-4">Loading Canvas...</div>}>
            <Canvas
              report={currentReport} allReports={openReports}
              activeReportId={activeReportId} onReportChange={(id) => {/*...*/}}
              onCloseReport={() => {/*...*/}} isExpanded={false}
              onToggleExpand={() => {/*...*/}}
            />
          </React.Suspense>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;