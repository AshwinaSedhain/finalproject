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
import SuggestionPrompts from "../components/SuggestionPrompts";

const DashboardPage = () => {
  const { token } = useAuth();
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);
  const isProcessingRef = useRef(false); // Lock to prevent parallel requests
  
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
  const [isChartExpanded, setIsChartExpanded] = useState(false);
  const [activeReportId, setActiveReportId] = useState(null);

  // Quick suggestion prompts (shorter versions for inline display)
  const quickSuggestions = [
    "Monthly revenue",
    "Top products",
    "Customer count",
    "Sales trends"
  ];

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
        id: initialConvoId, 
        title: 'Welcome!', 
        timestamp: new Date().toISOString(),
        messages: [{
          role: 'assistant',
          content: '👋 **Hello! I\'m your AI data assistant.**\n\nI can help you:\n- 📊 Analyze sales, revenue, and business metrics\n- 📈 Generate charts and visualizations\n- 💡 Answer questions about your data\n- 🔍 Provide insights and recommendations\n\nTry clicking on one of the suggestions below or ask me anything about your database!'
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

  const currentConversation = conversations[activeConversationId] || null;
  const messages = (currentConversation?.messages && Array.isArray(currentConversation.messages)) ? currentConversation.messages : [];
  const openReports = (currentConversation?.reports && Array.isArray(currentConversation.reports)) ? currentConversation.reports : [];
  const chatHistory = Object.values(conversations || {})
    .filter(c => c && c.id && c.title)
    .map(c => ({ id: c.id, title: c.title, timestamp: c.timestamp }))
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  
  // Set active report ID if not set or if reports changed
  useEffect(() => {
    if (openReports.length > 0) {
      if (!activeReportId || !openReports.find(r => r.id === activeReportId)) {
        setActiveReportId(openReports[openReports.length - 1].id);
      }
    } else {
      setActiveReportId(null);
    }
  }, [openReports, activeReportId]);
  
  const currentReport = openReports.find((r) => r.id === activeReportId);

  const handleSaveDbConfig = async (config) => {
    if (config && config.connectionString) {
      // Get old connection string before saving new one
      const oldConfig = dbConfig;
      const oldConnectionString = oldConfig?.connectionString;
      
      // Save new connection
      localStorage.setItem("dbConfig", JSON.stringify(config));
      setDbConfig(config);
      
      // Clear old connection from backend cache if it exists and is different
      if (oldConnectionString && oldConnectionString !== config.connectionString) {
        try {
          const { clearOldDatabaseConnection } = await import('../api');
          await clearOldDatabaseConnection(token, oldConnectionString);
          console.log('✓ Cleared old database connection');
        } catch (error) {
          console.warn('Failed to clear old connection (non-critical):', error);
        }
      }
    }
  };
  
  const handleSendMessage = async (prompt) => {
    // STRICT: Block if no prompt, no DB config, or already processing
    if (!prompt || !prompt.trim() || !dbConfig?.connectionString) {
      return;
    }
    
    // CRITICAL: Use ref to prevent race conditions - block if already processing
    if (isProcessingRef.current) {
      console.log('[Chat] Already processing a request, ignoring new message');
      return;
    }
    
    // If already loading (from state), stop the current generation first
    if (isLoading && abortControllerRef.current) {
      console.log('[Chat] Stopping previous generation before sending new message');
      abortControllerRef.current.abort();
      
      // Remove the last (incomplete) assistant message if it exists
      const convoId = activeConversationId;
      if (convoId) {
        setConversations(prev => {
          const convo = prev[convoId];
          if (convo && convo.messages && convo.messages.length > 0) {
            const lastMessage = convo.messages[convo.messages.length - 1];
            // Remove incomplete assistant message
            if (lastMessage && lastMessage.role === 'assistant') {
              return {
                ...prev,
                [convoId]: {
                  ...convo,
                  messages: convo.messages.slice(0, -1)
                }
              };
            }
          }
          return prev;
        });
      }
      
      setIsLoading(false);
      abortControllerRef.current = null;
      isProcessingRef.current = false;
      
      // Wait a bit to ensure cleanup
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    // Final check: prevent sending if still processing
    if (isProcessingRef.current || isLoading) {
      console.log('[Chat] Still processing, ignoring new message');
      return;
    }
    
    // Set processing lock IMMEDIATELY
    isProcessingRef.current = true;
    
    let convoId = activeConversationId;
    try {
      // Create new abort controller for this request
      abortControllerRef.current = new AbortController();
      const signal = abortControllerRef.current.signal;
      let isNewChat = false;
      
      if (!convoId || convoId === 'welcome-chat') {
        convoId = Date.now().toString();
        isNewChat = true;
      }
      
      if (isNewChat) {
        const newConvo = { 
          id: convoId, 
          title: prompt.substring(0, 50), 
          timestamp: new Date().toISOString(), 
          messages: [], 
          reports: [] 
        };
        setConversations(prev => ({ ...prev, [convoId]: newConvo }));
        setActiveConversationId(convoId);
      }
      
      const userMessage = { role: "user", content: prompt.trim() };
      
      // Set loading state IMMEDIATELY before any async operations
      setIsLoading(true);
      
      // Update conversations with user message
      setConversations(prev => {
        try {
          const current = prev[convoId] || { 
            id: convoId, 
            title: prompt.substring(0, 50), 
            timestamp: new Date().toISOString(), 
            messages: [], 
            reports: [] 
          };
          return {
            ...prev,
            [convoId]: {
              ...current,
              messages: [...(Array.isArray(current.messages) ? current.messages : []), userMessage]
            }
          };
        } catch (e) {
          console.error('Error updating conversations:', e);
          return prev;
        }
      });
      
      try {
        const aiResult = await sendChatMessage(prompt.trim(), token, signal, dbConfig?.connectionString);
        
        // Check if request was aborted or cancelled
        if (signal.aborted || (aiResult && aiResult.cancelled)) { 
          setIsLoading(false);
          abortControllerRef.current = null;
          isProcessingRef.current = false;
          return; 
        }
        
        // Check if the AI service returned an error (success: false)
        if (aiResult && aiResult.success === false) {
          const errorMessage = { 
            role: "assistant", 
            content: aiResult.response || "I'm experiencing issues with the AI service. Please try again in a moment. If the problem persists, contact support." 
          };
          setConversations(prev => {
            try {
              const convo = prev[convoId] || { 
                id: convoId, 
                title: prompt.substring(0, 50), 
                timestamp: new Date().toISOString(), 
                messages: [], 
                reports: [] 
              };
              return {
                ...prev,
                [convoId]: {
                  ...convo,
                  messages: [...(Array.isArray(convo.messages) ? convo.messages : []), errorMessage]
                }
              };
            } catch (e) {
              console.error('Error updating conversations with error message:', e);
              return prev;
            }
          });
          return;
        }
      
        let chartData = null;
        if (aiResult.visualization) { 
        try { 
          chartData = JSON.parse(aiResult.visualization); 
        } catch (e) { 
          console.error("Failed to parse viz JSON", e); 
        } 
        }
        
        const newReportId = chartData ? Date.now().toString() : null;
        const aiMessage = { 
        role: "assistant", 
        content: aiResult.response || "I apologize, but I couldn't generate a response. Please try again.", 
        reportId: newReportId 
        };
        const newReport = chartData ? { 
        id: newReportId, 
        title: prompt.substring(0, 50), 
        type: aiResult.chart_type || 'chart', 
        chartData 
        } : null;
        
        setConversations(prev => {
        try {
          const convo = prev[convoId] || { 
            id: convoId, 
            title: prompt.substring(0, 50), 
            timestamp: new Date().toISOString(), 
            messages: [], 
            reports: [] 
          };
          const updatedReports = newReport ? [...(Array.isArray(convo.reports) ? convo.reports : []), newReport] : (Array.isArray(convo.reports) ? convo.reports : []);
          return {
            ...prev,
            [convoId]: {
              ...convo,
              messages: [...(Array.isArray(convo.messages) ? convo.messages : []), aiMessage],
              reports: updatedReports
            }
          };
        } catch (e) {
          console.error('Error updating conversations with AI response:', e);
          return prev;
        }
        });
        
        // Set the new report as active if it was created
        if (newReport) {
          setActiveReportId(newReportId);
        }
      } catch (error) {
      console.error('Error sending message:', error);
      if (error.name !== 'AbortError') {
        const errorMessage = { 
          role: "assistant", 
          content: `Sorry, an error occurred: ${error.message || 'Please try again.'}` 
        };
        setConversations(prev => {
          try {
            const convo = prev[convoId] || { 
              id: convoId, 
              title: prompt.substring(0, 50), 
              timestamp: new Date().toISOString(), 
              messages: [], 
              reports: [] 
            };
            return {
              ...prev,
              [convoId]: {
                ...convo,
                messages: [...(Array.isArray(convo.messages) ? convo.messages : []), errorMessage]
              }
            };
          } catch (e) {
            console.error('Error updating conversations with error message:', e);
            return prev;
          }
        });
      }
      } finally {
        // CRITICAL: Always release the lock - ensure this happens after all async operations
        // Use a small delay to ensure state is properly updated
        setTimeout(() => {
          setIsLoading(false);
          abortControllerRef.current = null;
          isProcessingRef.current = false;
        }, 50);
      }
    } catch (outerError) {
      console.error('Error in handleSendMessage:', outerError);
      // Ensure state is reset even on outer errors
      setIsLoading(false);
      abortControllerRef.current = null;
      isProcessingRef.current = false;
    }
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    
    // Remove the last (incomplete) assistant message if it exists
    const convoId = activeConversationId;
    if (convoId) {
      setConversations(prev => {
        const convo = prev[convoId];
        if (convo && convo.messages && convo.messages.length > 0) {
          const lastMessage = convo.messages[convo.messages.length - 1];
          // Remove incomplete assistant message
          if (lastMessage && lastMessage.role === 'assistant' && (!lastMessage.content || lastMessage.content.trim() === '')) {
            return {
              ...prev,
              [convoId]: {
                ...convo,
                messages: convo.messages.slice(0, -1)
              }
            };
          }
        }
        return prev;
      });
    }
    
    // Release all locks
    setIsLoading(false);
    isProcessingRef.current = false;
  };

  const handleEditMessage = async (messageIndex, newContent) => {
    if (!newContent.trim() || isLoading || !dbConfig?.connectionString) return;
    
    const convoId = activeConversationId;
    if (!convoId) return;

    // Remove all messages after the edited message (including the assistant's response)
    const convo = conversations[convoId];
    if (!convo) return;

    // Truncate messages up to (but not including) the edited message
    // This removes the edited message and all subsequent messages
    const updatedMessages = convo.messages.slice(0, messageIndex);
    
    // Also remove any reports that were generated after this message
    const updatedReports = convo.reports || [];
    
    // Update conversation with truncated messages and reports
    setConversations(prev => ({
      ...prev,
      [convoId]: {
        ...convo,
        messages: updatedMessages,
        reports: updatedReports
      }
    }));

    // Clear active report if it was removed
    setActiveReportId(null);

    // Small delay to ensure state is updated, then resend the edited message
    setTimeout(() => {
      handleSendMessage(newContent);
    }, 100);
  };

  const handleSelectChat = (chat) => { setActiveConversationId(chat.id); setSidebarOpen(false); };
  const handleNewChat = () => {
    const newId = Date.now().toString();
    const welcomeMessage = {
      role: 'assistant',
      content: '👋 **Hello! I\'m your AI data assistant.**\n\nI can help you:\n- 📊 Analyze sales, revenue, and business metrics\n- 📈 Generate charts and visualizations\n- 💡 Answer questions about your data\n- 🔍 Provide insights and recommendations\n\nTry clicking on one of the suggestions below or ask me anything about your database!'
    };
    const newConvo = { 
      id: newId, 
      title: "New Conversation", 
      timestamp: new Date().toISOString(), 
      messages: [welcomeMessage], 
      reports: [] 
    };
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
      <Navbar 
        onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
        activeView="chat"
        onChatClick={() => {}} // Already on chat page
      />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)}
          chatHistory={chatHistory} onSelectChat={handleSelectChat}
          activeChatId={activeConversationId} onNewChat={handleNewChat}
          onDeleteChat={handleDeleteChat} showCloseButton={true}
        />
        <div className={`flex-1 flex flex-col`}>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages && messages.length > 0 ? (
              <>
                {messages.map((msg, i) => {
                  if (!msg || !msg.role) return null;
                  // Find the last user message index
                  const lastUserMessageIndex = messages
                    .map((m, idx) => (m && m.role === 'user') ? idx : -1)
                    .filter(idx => idx !== -1)
                    .pop();
                  const isLastUserMessage = msg.role === 'user' && i === lastUserMessageIndex;
                  return (
                    <ChatMessage 
                      key={`msg-${i}-${msg.content?.substring(0, 10) || i}`} 
                      message={msg} 
                      messageIndex={i}
                      isLastUserMessage={isLastUserMessage}
                      onEdit={handleEditMessage}
                    />
                  );
                })}
                {isLoading && <ChatMessage message={{ role: 'assistant', content: '' }} isLoading={true} />}
              </>
            ) : !isLoading ? (
              <div className="flex items-center justify-center h-full">
                <SuggestionPrompts 
                  onSelectPrompt={handleSendMessage} 
                  disabled={!dbConfig || isLoading || isProcessingRef.current}
                />
              </div>
            ) : null}
            <div ref={messagesEndRef} />
          </div>
          <ChatInput 
            onSend={handleSendMessage} 
            disabled={!dbConfig || isLoading} 
            isLoading={isLoading} 
            onStop={handleStop}
            suggestions={messages.length > 0 && !isLoading ? quickSuggestions : []}
          />
        </div>
        {openReports.length > 0 && (
          <React.Suspense fallback={<div className="w-1/2 p-4">Loading Canvas...</div>}>
            <Canvas
              report={currentReport}
              allReports={openReports}
              activeReportId={activeReportId}
              onReportChange={(id) => {
                setActiveReportId(id);
              }}
              onCloseReport={(reportId) => {
                setConversations(prev => {
                  const convo = prev[activeConversationId];
                  if (!convo) return prev;
                  const updatedReports = convo.reports.filter(r => r.id !== reportId);
                  
                  // If closing the active report, switch to the last remaining one
                  if (activeReportId === reportId && updatedReports.length > 0) {
                    setActiveReportId(updatedReports[updatedReports.length - 1].id);
                  } else if (updatedReports.length === 0) {
                    setActiveReportId(null);
                  }
                  
                  return {
                    ...prev,
                    [activeConversationId]: {
                      ...convo,
                      reports: updatedReports
                    }
                  };
                });
              }}
              isExpanded={isChartExpanded}
              onToggleExpand={() => setIsChartExpanded(!isChartExpanded)}
            />
          </React.Suspense>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;