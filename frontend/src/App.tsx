import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  ArrowUp,
  BarChart3,
  Bell,
  Check,
  CheckCircle2,
  ChevronDown,
  FileText,
  Globe,
  History as HistoryIcon,
  Home,
  Image as ImageIcon,
  Languages,
  LayoutDashboard,
  Link as LinkIcon,
  LogOut,
  Menu,
  Mic,
  Paperclip,
  Play,
  Plus,
  Search,
  Send,
  Settings,
  Shield,
  Sparkles,
  Square,
  User,
  Volume2,
  Copy,
  Download,
  WandSparkles,
  X,
  Zap,
} from 'lucide-react';
import './App.css';

type Page = 'home' | 'investigate' | 'history' | 'analytics' | 'how' | 'architecture' | 'notifications' | 'profile' | 'settings';
type Language = 'Auto' | 'English' | 'Hindi' | 'Marathi' | 'Hinglish / Roman';
type InputMode = 'text' | 'link' | 'file' | 'screenshot';
type ChatMessage = { id: number; role: 'user' | 'assistant'; text: string; attachment?: string };
type ImportantOnly = { situation?: string; risk?: string; deadline?: string; required_documents?: string[]; missing_requirement?: string; action?: string; consequence?: string; next_step?: string };
type ReportData = {
  summary?: string; situation?: string; risk_score?: number; risk_level?: string; risk_factors?: string[]; consequences?: string[]; what_to_do?: string[]; what_not_to_do?: string[]; action_plan?: string[]; important_only?: ImportantOnly;
  document_insights?: { situation?: string; deadline?: string; required_documents?: string[]; action?: string; consequence?: string; missing_requirement?: string; action_plan?: string[] };
  agent_activity?: string[]; confidence?: number; evaluation_status?: string; adaptation_required?: boolean; language?: string; script?: string; input_type?: string; user_goal?: string; session_id?: string;
};
type UserProfile = { name: string; email: string; password?: string; language: Language; script: 'Auto' | 'Devanagari' | 'Latin'; voiceInput: boolean; tts: boolean; largeText: boolean; highContrast: boolean; reducedMotion: boolean; notifications: boolean };
type HistoryItem = { id: string; date: string; summary: string; language: string; risk: string; status: string };

const API_BASE = '';
const HISTORY_KEY = 'bhashalife_history_v3';
const USER_KEY = 'bhashalife_user_v3';
const AUTH_KEY = 'bhashalife_auth_v3';

const LANGS: Language[] = ['Auto', 'English', 'Hindi', 'Marathi', 'Hinglish / Roman'];

const copy: Record<string, Record<string, string>> = {
  English: {
    home: 'Home', investigate: 'Investigate', history: 'History', analytics: 'Analytics', how: 'How It Works', architecture: 'Architecture', notifications: 'Notifications', profile: 'Profile', settings: 'Settings', logout: 'Logout',
    live: 'Live Intelligence', overview: 'Overview', important: 'Important Only', todo: 'What To Do', situation: 'Situation', risk: 'Risk', consequences: 'What Could Happen', next: 'What Should You Do Now?', activity: 'Agent Activity', confidence: 'Confidence', resolution: 'Resolution Readiness', send: 'Send', upload: 'Upload file', screenshot: 'Screenshot', link: 'Paste link', text: 'Enter text', voice: 'Voice input',
    ask: 'Ask BhashaLife anything...', start: 'Start a conversation', greeting: 'Namaste! 👋 Tell me what is confusing. I will help you understand what matters and what to do next.', investigateDesc: 'Upload a notice, message, screenshot or link and let the agent work through it with you.', newInvestigation: 'New investigation', engine: 'Engine ready', analyzing: 'Investigating',
    workspaceTitle:'Investigation workspace',copyReport:'Copy report',exportReport:'Export report',liveBadge:'Live',latest:'Latest',agentStep:'Agent step',deadline:'Deadline',required:'Required',consequence:'Consequence',nextStep:'Next step',yourActionPlan:'YOUR ACTION PLAN',moveConfidence:'Move forward with confidence.',whatNotToDo:'What not to do',notAvailable:'Not available',noneIdentified:'None identified',focusAction:'Focus on the action, deadline and consequence.',
  },
  Hindi: {
    home: 'होम', investigate: 'जांच करें', history: 'इतिहास', analytics: 'विश्लेषण', how: 'यह कैसे काम करता है', architecture: 'आर्किटेक्चर', notifications: 'सूचनाएं', profile: 'प्रोफ़ाइल', settings: 'सेटिंग्स', logout: 'लॉग आउट',
    live: 'लाइव इंटेलिजेंस', overview: 'अवलोकन', important: 'ज़रूरी बातें', todo: 'क्या करना है', situation: 'स्थिति', risk: 'जोखिम', consequences: 'क्या हो सकता है', next: 'अब आपको क्या करना चाहिए?', activity: 'एजेंट गतिविधि', confidence: 'विश्वास स्तर', resolution: 'समाधान तैयारी', send: 'भेजें', upload: 'फ़ाइल अपलोड', screenshot: 'स्क्रीनशॉट', link: 'लिंक डालें', text: 'टेक्स्ट लिखें', voice: 'आवाज़ से पूछें',
    ask: 'BhashaLife से कुछ भी पूछें...', start: 'बातचीत शुरू करें', greeting: 'नमस्ते! 👋 जो बात समझ नहीं आ रही है, उसे बताइए। मैं बताऊंगा कि क्या महत्वपूर्ण है और आगे क्या करना है।', investigateDesc: 'नोटिस, संदेश, स्क्रीनशॉट या लिंक दें और एजेंट आपके साथ पूरी स्थिति समझेगा।', newInvestigation: 'नई जांच', engine: 'इंजन तैयार', analyzing: 'जांच चल रही है',
    workspaceTitle:'जांच कार्यक्षेत्र',copyReport:'रिपोर्ट कॉपी करें',exportReport:'रिपोर्ट एक्सपोर्ट करें',liveBadge:'लाइव',latest:'नवीनतम',agentStep:'एजेंट चरण',deadline:'अंतिम तारीख',required:'आवश्यक',consequence:'परिणाम',nextStep:'अगला कदम',yourActionPlan:'आपकी कार्य योजना',moveConfidence:'स्पष्ट अगले कदम के साथ आगे बढ़ें।',whatNotToDo:'क्या न करें',notAvailable:'उपलब्ध नहीं',noneIdentified:'कुछ नहीं मिला',focusAction:'कार्रवाई, अंतिम तारीख और परिणाम पर ध्यान दें।',
  },
  Marathi: {
    home: 'मुख्यपृष्ठ', investigate: 'तपासणी', history: 'इतिहास', analytics: 'विश्लेषण', how: 'हे कसे काम करते', architecture: 'आर्किटेक्चर', notifications: 'सूचना', profile: 'प्रोफाइल', settings: 'सेटिंग्ज', logout: 'लॉग आउट',
    live: 'लाइव्ह इंटेलिजन्स', overview: 'आढावा', important: 'महत्त्वाचे', todo: 'काय करावे', situation: 'परिस्थिती', risk: 'धोका', consequences: 'काय होऊ शकते', next: 'आता तुम्ही काय करावे?', activity: 'एजंट क्रिया', confidence: 'विश्वास पातळी', resolution: 'निराकरण तयारी', send: 'पाठवा', upload: 'फाइल अपलोड', screenshot: 'स्क्रीनशॉट', link: 'लिंक द्या', text: 'मजकूर लिहा', voice: 'आवाजाने विचारा',
    ask: 'BhashaLife ला काहीही विचारा...', start: 'संवाद सुरू करा', greeting: 'नमस्कार! 👋 तुम्हाला जे समजत नाही ते सांगा. काय महत्त्वाचे आहे आणि पुढे काय करायचे ते मी समजावून सांगेन.', investigateDesc: 'नोटीस, संदेश, स्क्रीनशॉट किंवा लिंक द्या आणि एजंट तुमच्यासोबत संपूर्ण परिस्थिती समजून घेईल.', newInvestigation: 'नवीन तपासणी', engine: 'इंजिन तयार', analyzing: 'तपासणी सुरू आहे',
    workspaceTitle:'तपासणी कार्यक्षेत्र',copyReport:'रिपोर्ट कॉपी करा',exportReport:'रिपोर्ट एक्सपोर्ट करा',liveBadge:'लाइव्ह',latest:'नवीनतम',agentStep:'एजंट टप्पा',deadline:'अंतिम तारीख',required:'आवश्यक',consequence:'परिणाम',nextStep:'पुढील कृती',yourActionPlan:'तुमची कृती योजना',moveConfidence:'स्पष्ट पुढील कृतीसह पुढे जा.',whatNotToDo:'काय करू नये',notAvailable:'उपलब्ध नाही',noneIdentified:'काही आढळले नाही',focusAction:'कृती, अंतिम तारीख आणि परिणाम यावर लक्ष द्या.',
  },
  'Hinglish / Roman': {
    home: 'Home', investigate: 'Investigate', history: 'History', analytics: 'Analytics', how: 'How It Works', architecture: 'Architecture', notifications: 'Notifications', profile: 'Profile', settings: 'Settings', logout: 'Logout',
    live: 'Live Intelligence', overview: 'Overview', important: 'Important Only', todo: 'Kya Karna Hai', situation: 'Situation', risk: 'Risk', consequences: 'Kya Ho Sakta Hai', next: 'Ab Aapko Kya Karna Chahiye?', activity: 'Agent Activity', confidence: 'Confidence', resolution: 'Resolution Readiness', send: 'Bhejein', upload: 'File upload', screenshot: 'Screenshot', link: 'Link paste karein', text: 'Text likhein', voice: 'Voice se poochhein',
    ask: 'BhashaLife se kuch bhi poochhein...', start: 'Conversation start karein', greeting: 'Namaste! 👋 Jo confusing hai woh batao. Main samjhaunga kya important hai aur next kya karna hai.', investigateDesc: 'Notice, message, screenshot ya link do aur agent tumhare saath poori situation samjhega.', newInvestigation: 'New investigation', engine: 'Engine ready', analyzing: 'Investigating',
    workspaceTitle:'Investigation workspace',copyReport:'Report copy karein',exportReport:'Report export karein',liveBadge:'Live',latest:'Latest',agentStep:'Agent step',deadline:'Deadline',required:'Required',consequence:'Consequence',nextStep:'Next step',yourActionPlan:'AAPKA ACTION PLAN',moveConfidence:'Clear next step ke saath aage badhein.',whatNotToDo:'Kya nahi karna hai',notAvailable:'Available nahi',noneIdentified:'Kuch identify nahi hua',focusAction:'Action, deadline aur consequence par focus karein.',
  },
};

function baseLanguage(language: string): keyof typeof copy {
  if (language === 'Hindi') return 'Hindi';
  if (language === 'Marathi') return 'Marathi';
  if (language === 'Hinglish / Roman') return 'Hinglish / Roman';
  return 'English';
}

const extraCopy: Record<string, Record<string,string>> = {
  English: {conversation:'Conversation',autoLanguage:'Auto language',you:'You',agentLoop:'Observe · Decide · Act · Evaluate · Adapt',decisionSupport:'Decision support, not a guarantee',waitingTitle:'Live Intelligence is waiting',waitingText:'Once you share something, the agent will turn it into a clear situation, risk and next action.',situationUnderstood:'Situation understood',openActionPlan:'Open action plan',evaluationProgress:'Evaluation in progress',agentStep:'Agent step',latest:'Latest',importantOnly:'IMPORTANT ONLY',deadline:'Deadline',required:'Required',consequence:'Consequence',nextStep:'Next step',noData:'Not available',noneIdentified:'None identified',actionPlan:'YOUR ACTION PLAN',actionPlanTitle:'Move forward with confidence.',whatNotToDo:'What not to do',uploadDesc:'PDF, DOCX, TXT, image',screenshotDesc:'Image analysis + OCR',linkDesc:'URL intelligence',textDesc:'Paste any message',linkPlaceholder:'Paste a link to analyze...',composerNote:'BhashaLife can make mistakes. Verify important information.',voiceInput:'Voice input',stopVoice:'Stop voice input',focusAction:'Focus on the action, deadline and consequence.',reviewActionPlan:'Review the recommended action plan.',workspace:'Investigation workspace',liveBadge:'Live',copyReport:'Copy report',downloadReport:'Export report',copied:'Copied!',copyFailed:'Copy failed',reportTitle:'BhashaLife AI — Live Intelligence Report'},
  Hindi: {conversation:'बातचीत',autoLanguage:'ऑटो भाषा',you:'आप',agentLoop:'देखें · निर्णय लें · कार्रवाई करें · जांचें · अनुकूलित करें',decisionSupport:'निर्णय में सहायता, गारंटी नहीं',waitingTitle:'लाइव इंटेलिजेंस तैयार है',waitingText:'कुछ साझा करने के बाद एजेंट स्थिति, जोखिम और अगला कदम स्पष्ट करेगा।',situationUnderstood:'स्थिति समझ ली गई',openActionPlan:'कार्य योजना खोलें',evaluationProgress:'मूल्यांकन चल रहा है',agentStep:'एजेंट चरण',latest:'नवीनतम',importantOnly:'ज़रूरी बातें',deadline:'अंतिम तारीख',required:'ज़रूरी',consequence:'परिणाम',nextStep:'अगला कदम',noData:'उपलब्ध नहीं',noneIdentified:'कुछ नहीं मिला',actionPlan:'आपकी कार्य योजना',actionPlanTitle:'आत्मविश्वास के साथ आगे बढ़ें।',whatNotToDo:'क्या न करें',uploadDesc:'PDF, DOCX, TXT, इमेज',screenshotDesc:'इमेज विश्लेषण + OCR',linkDesc:'URL जांच',textDesc:'कोई भी संदेश डालें',linkPlaceholder:'विश्लेषण के लिए लिंक डालें...',composerNote:'BhashaLife से कभी-कभी गलती हो सकती है। महत्वपूर्ण जानकारी सत्यापित करें।',voiceInput:'आवाज़ से इनपुट',stopVoice:'आवाज़ रोकें',focusAction:'कार्रवाई, अंतिम तारीख और परिणाम पर ध्यान दें।',reviewActionPlan:'सुझाई गई कार्य योजना देखें।',workspace:'जांच कार्यक्षेत्र',liveBadge:'लाइव',copyReport:'रिपोर्ट कॉपी करें',downloadReport:'रिपोर्ट एक्सपोर्ट करें',copied:'कॉपी हो गया!',copyFailed:'कॉपी नहीं हो सका',reportTitle:'BhashaLife AI — लाइव इंटेलिजेंस रिपोर्ट'},
  Marathi: {conversation:'संवाद',autoLanguage:'ऑटो भाषा',you:'तुम्ही',agentLoop:'निरीक्षण · निर्णय · कृती · मूल्यांकन · बदल',decisionSupport:'निर्णयासाठी मदत, हमी नाही',waitingTitle:'लाइव्ह इंटेलिजन्स तयार आहे',waitingText:'तुम्ही काही शेअर केल्यानंतर एजंट परिस्थिती, धोका आणि पुढील कृती स्पष्ट करेल.',situationUnderstood:'परिस्थिती समजली',openActionPlan:'कृती योजना उघडा',evaluationProgress:'मूल्यांकन सुरू आहे',agentStep:'एजंट टप्पा',latest:'नवीनतम',importantOnly:'महत्त्वाचे',deadline:'अंतिम तारीख',required:'आवश्यक',consequence:'परिणाम',nextStep:'पुढील कृती',noData:'उपलब्ध नाही',noneIdentified:'काहीही आढळले नाही',actionPlan:'तुमची कृती योजना',actionPlanTitle:'आत्मविश्वासाने पुढे जा.',whatNotToDo:'काय करू नये',uploadDesc:'PDF, DOCX, TXT, इमेज',screenshotDesc:'इमेज विश्लेषण + OCR',linkDesc:'URL तपासणी',textDesc:'कोणताही संदेश टाका',linkPlaceholder:'तपासणीसाठी लिंक द्या...',composerNote:'BhashaLife कडून कधीकधी चूक होऊ शकते. महत्त्वाची माहिती पडताळून पहा.',voiceInput:'आवाजातून इनपुट',stopVoice:'आवाज थांबवा',focusAction:'कृती, अंतिम तारीख आणि परिणामावर लक्ष द्या.',reviewActionPlan:'सुचवलेली कृती योजना पहा.',workspace:'तपासणी कार्यक्षेत्र',liveBadge:'लाइव्ह',copyReport:'रिपोर्ट कॉपी करा',downloadReport:'रिपोर्ट एक्सपोर्ट करा',copied:'कॉपी झाले!',copyFailed:'कॉपी करता आले नाही',reportTitle:'BhashaLife AI — लाइव्ह इंटेलिजन्स रिपोर्ट'},
  'Hinglish / Roman': {conversation:'Conversation',autoLanguage:'Auto language',you:'Aap',agentLoop:'Observe · Decide · Act · Evaluate · Adapt',decisionSupport:'Decision support, guarantee nahi',waitingTitle:'Live Intelligence ready hai',waitingText:'Kuch share karne ke baad agent situation, risk aur next action clear karega.',situationUnderstood:'Situation samajh li gayi',openActionPlan:'Action plan dekhein',evaluationProgress:'Evaluation chal raha hai',agentStep:'Agent step',latest:'Latest',importantOnly:'IMPORTANT ONLY',deadline:'Last date',required:'Required',consequence:'Result',nextStep:'Next step',noData:'Available nahi',noneIdentified:'Kuch nahi mila',actionPlan:'YOUR ACTION PLAN',actionPlanTitle:'Confidence ke saath aage badho.',whatNotToDo:'Kya nahi karna hai',uploadDesc:'PDF, DOCX, TXT, image',screenshotDesc:'Image analysis + OCR',linkDesc:'URL checking',textDesc:'Koi bhi message paste karo',linkPlaceholder:'Analyze karne ke liye link paste karo...',composerNote:'BhashaLife se kabhi-kabhi mistake ho sakti hai. Important information verify karo.',voiceInput:'Voice input',stopVoice:'Voice stop karo',focusAction:'Action, last date aur result par focus karo.',reviewActionPlan:'Recommended action plan dekho.',workspace:'Investigation workspace',liveBadge:'Live',copyReport:'Report copy karo',downloadReport:'Report export karo',copied:'Copy ho gaya!',copyFailed:'Copy nahi hua',reportTitle:'BhashaLife AI — Live Intelligence Report'}
};

function t(language: Language, key: string) {
  return extraCopy[baseLanguage(language)]?.[key] || copy[baseLanguage(language)][key] || copy.English[key] || key;
}

function detectScriptFor(language: Language, selected: UserProfile['script']) {
  if (selected !== 'Auto') return selected;
  return language === 'Hindi' || language === 'Marathi' ? 'Devanagari' : 'Latin';
}

function useReveal() {
  useEffect(() => {
    const nodes = document.querySelectorAll<HTMLElement>('[data-reveal]');
    if (!('IntersectionObserver' in window)) { nodes.forEach(n => n.classList.add('revealed')); return; }
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('revealed'); observer.unobserve(entry.target); }
    }), { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    nodes.forEach((node,index) => {
      if (node.classList.contains('reveal-item')) node.style.setProperty('--reveal-delay', `${Math.min(index % 6,5) * 80}ms`);
      observer.observe(node);
    });
    return () => observer.disconnect();
  }, []);
}

function App() {
  const [page, setPage] = useState<Page>('home');
  const [landing, setLanding] = useState(true);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');
  const [showAuth, setShowAuth] = useState(false);
  const [isGuest, setIsGuest] = useState(false);
  const [profile, setProfile] = useState<UserProfile>(() => {
    try { return JSON.parse(localStorage.getItem(USER_KEY) || '') as UserProfile; } catch { return { name: '', email: '', language: 'Auto', script: 'Auto', voiceInput: true, tts: true, largeText: false, highContrast: false, reducedMotion: false, notifications: true }; }
  });
  const [loggedIn, setLoggedIn] = useState(() => localStorage.getItem(AUTH_KEY) === 'true');
  const [authName, setAuthName] = useState('');
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [mobileNav, setMobileNav] = useState(false);
  const [language, setLanguage] = useState<Language>(profile.language || 'Auto');
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
  const [showInputMenu, setShowInputMenu] = useState(false);
  const [inputMode, setInputMode] = useState<InputMode>('text');
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [report, setReport] = useState<ReportData | null>(null);
  const [activeTab, setActiveTab] = useState<'Overview' | 'Important' | 'What To Do'>('Overview');
  const [history, setHistory] = useState<HistoryItem[]>(() => { try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); } catch { return []; } });
  const [notifications, setNotifications] = useState<{ id: string; title: string; body: string; type: string; read: boolean }[]>([]);
  const [voiceListening, setVoiceListening] = useState(false);
  const [voiceError, setVoiceError] = useState('');
  const [searchHistory, setSearchHistory] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const screenshotInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);
  useReveal();

  const detectedUiLanguage = (report?.language && report.language !== 'Auto' ? report.language : null) as Language | null;
  const uiLanguage: Language = language === 'Auto' ? (detectedUiLanguage || (profile.language === 'Auto' ? 'English' : profile.language)) : language;

  useEffect(() => {
    if (loggedIn) setLanding(false);
  }, [loggedIn]);

  useEffect(() => {
    localStorage.setItem(USER_KEY, JSON.stringify({ ...profile, language }));
  }, [profile, language]);

  useEffect(() => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 50)));
  }, [history]);

  useEffect(() => {
    document.documentElement.classList.toggle('large-text', profile.largeText);
    document.documentElement.classList.toggle('high-contrast', profile.highContrast);
    document.documentElement.classList.toggle('reduced-motion', profile.reducedMotion);
  }, [profile.largeText, profile.highContrast, profile.reducedMotion]);

  const setPageAndClose = (next: Page) => { setPage(next); setLanding(false); setMobileNav(false); };

  const startApp = () => { setLanding(false); setShowAuth(true); setAuthMode('signup'); };
  const continueGuest = () => { setLanding(false); setIsGuest(true); setLoggedIn(true); setPage('home'); localStorage.setItem(AUTH_KEY, 'true'); };

  const handleAuth = (event: React.FormEvent) => {
    event.preventDefault();
    setAuthError('');
    if (!authEmail || !authPassword || (authMode === 'signup' && !authName)) {
      setAuthError('Please complete all required fields.'); return;
    }
    const stored = localStorage.getItem('bhashalife_account_v3');
    if (authMode === 'signup') {
      localStorage.setItem('bhashalife_account_v3', JSON.stringify({ name: authName, email: authEmail, password: authPassword }));
      const nextProfile = { ...profile, name: authName, email: authEmail };
      setProfile(nextProfile); setLoggedIn(true); setIsGuest(false); localStorage.setItem(AUTH_KEY, 'true'); setShowAuth(false); setPage('home');
    } else {
      if (!stored) { setAuthError('No local demo account found. Please sign up first.'); return; }
      const account = JSON.parse(stored);
      if (account.email !== authEmail || account.password !== authPassword) { setAuthError('Email or password is incorrect.'); return; }
      setProfile(p => ({ ...p, name: account.name, email: account.email })); setLoggedIn(true); setIsGuest(false); localStorage.setItem(AUTH_KEY, 'true'); setShowAuth(false); setPage('home');
    }
  };

  const logout = () => { setLoggedIn(false); setIsGuest(false); localStorage.removeItem(AUTH_KEY); setLanding(true); setPage('home'); };

  const selectLanguage = (value: Language) => {
    setLanguage(value);
    setProfile(p => ({ ...p, language: value }));
    setShowLanguageMenu(false);
  };

  const useQuickAction = (text: string) => { setMessage(text); setPage('investigate'); };

  const openFilePicker = () => { setShowInputMenu(false); setInputMode('file'); fileInputRef.current?.click(); };
  const openScreenshotPicker = () => { setShowInputMenu(false); setInputMode('screenshot'); screenshotInputRef.current?.click(); };
  const selectLinkMode = () => { setShowInputMenu(false); setInputMode('link'); setMessage(''); };
  const selectTextMode = () => { setShowInputMenu(false); setInputMode('text'); setMessage(''); };
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => { const file = event.target.files?.[0]; if (file) { setSelectedFile(file); setInputMode('file'); } };
  const handleScreenshotChange = (event: React.ChangeEvent<HTMLInputElement>) => { const file = event.target.files?.[0]; if (file) { setSelectedFile(file); setInputMode('screenshot'); } };

  const startVoice = () => {
    setVoiceError('');
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) { setVoiceError('Voice input is not supported in this browser. Try Chrome or Edge.'); return; }
    if (voiceListening) { recognitionRef.current?.stop(); return; }
    const recognition = new SpeechRecognition();
    recognition.lang = uiLanguage === 'Hindi' ? 'hi-IN' : uiLanguage === 'Marathi' ? 'mr-IN' : 'en-IN';
    recognition.continuous = false; recognition.interimResults = true;
    recognition.onstart = () => setVoiceListening(true);
    recognition.onend = () => setVoiceListening(false);
    recognition.onerror = () => { setVoiceListening(false); setVoiceError('Voice input stopped. Please try again.'); };
    recognition.onresult = (event: any) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) transcript += event.results[i][0].transcript;
      setMessage(transcript);
    };
    recognitionRef.current = recognition;
    recognition.start();
  };

  const speak = (text: string) => {
    if (!profile.tts || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = uiLanguage === 'Hindi' ? 'hi-IN' : uiLanguage === 'Marathi' ? 'mr-IN' : 'en-IN';
    window.speechSynthesis.speak(utterance);
  };

  const newInvestigation = () => {
    setSessionId(null); setReport(null); setMessages([]); setMessage(''); setSelectedFile(null); setInputMode('text'); setPage('investigate');
  };

  const analyze = async () => {
    const trimmed = message.trim();
    if (!trimmed && !selectedFile) return;
    setLoading(true); setPage('investigate'); setShowInputMenu(false); setShowLanguageMenu(false);
    const displayed = trimmed || `Analyze this ${inputMode === 'screenshot' ? 'screenshot' : 'document'}.`;
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', text: displayed, attachment: selectedFile?.name }]);
    const fileToSend = selectedFile;
    setMessage(''); setSelectedFile(null); setInputMode('text');
    if (fileInputRef.current) fileInputRef.current.value = ''; if (screenshotInputRef.current) screenshotInputRef.current.value = '';
    try {
      const formData = new FormData();
      formData.append('text', trimmed); formData.append('context', ''); formData.append('language', language);
      if (sessionId) formData.append('session_id', sessionId); if (fileToSend) formData.append('file', fileToSend);
      const response = await fetch(`${API_BASE}/api/analyze`, { method: 'POST', body: formData });
      if (!response.ok) throw new Error(`API request failed: ${response.status}`);
      const data = await response.json(); const returnedState: ReportData = data.state || data;
      const normalized: ReportData = { ...returnedState, summary: data.summary || returnedState.summary, situation: data.situation || returnedState.situation, risk_score: data.risk_score ?? returnedState.risk_score, risk_level: data.risk_level || returnedState.risk_level, risk_factors: data.risk_factors || returnedState.risk_factors || [], consequences: data.consequences || returnedState.consequences || [], what_to_do: data.what_to_do || returnedState.what_to_do || [], what_not_to_do: data.what_not_to_do || returnedState.what_not_to_do || [], action_plan: data.action_plan || returnedState.action_plan || [], important_only: data.important_only || returnedState.important_only || {}, document_insights: data.document_insights || returnedState.document_insights, agent_activity: data.agent_activity || returnedState.agent_activity || [], confidence: data.confidence ?? returnedState.confidence, evaluation_status: data.evaluation_status || returnedState.evaluation_status, adaptation_required: data.adaptation_required ?? returnedState.adaptation_required, user_goal: data.user_goal || returnedState.user_goal, session_id: data.session_id || returnedState.session_id, language: data.language || returnedState.language || language };
      setReport(normalized); setSessionId(data.session_id || returnedState.session_id || null);
      const assistantText = buildAssistantResponse(normalized);
      setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', text: assistantText }]);
      const item: HistoryItem = { id: crypto.randomUUID?.() || String(Date.now()), date: new Date().toLocaleString(), summary: normalized.situation || normalized.summary || 'Investigation completed', language: normalized.language || language, risk: normalized.risk_level || 'Unknown', status: normalized.evaluation_status === 'success' ? 'Resolved' : 'Reviewed' };
      setHistory(prev => [item, ...prev]);
      if (normalized.adaptation_required) setNotifications(prev => [{ id: String(Date.now()), title: 'Investigation adapted', body: 'New information changed the recommended plan.', type: 'update', read: false }, ...prev]);
      if ((normalized.risk_level === 'HIGH' || normalized.risk_level === 'CRITICAL')) setNotifications(prev => [{ id: String(Date.now() + 3), title: 'High-priority action', body: 'Review the Life Shield recommendations now.', type: 'action', read: false }, ...prev]);
    } catch (error) {
      console.error(error); setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', text: localizeStatic('I could not connect to the BhashaLife engine. Please make sure the FastAPI backend is running on port 8001.', uiLanguage) }]);
    } finally { setLoading(false); }
  };

  const filteredHistory = useMemo(() => history.filter(item => `${item.summary} ${item.language} ${item.risk}`.toLowerCase().includes(searchHistory.toLowerCase())), [history, searchHistory]);

  if (landing && !loggedIn) return <LandingPage onStart={startApp} onGuest={continueGuest} onLogin={() => { setAuthMode('login'); setShowAuth(true); }} />;

  return (
    <div className={`app-shell theme-${page} ${profile.highContrast ? 'contrast' : ''}`}>
      <aside className={`sidebar ${mobileNav ? 'open' : ''}`}>
        <div className="side-brand" onClick={() => setPageAndClose('home')}><div className="brand-mark"><Shield size={22} /></div><div><strong>BhashaLife <span>AI</span></strong><small>Life intelligence</small></div></div>
        <div className="side-section-label">WORKSPACE</div>
        <NavButton icon={<Home size={18} />} label={t(language, 'home')} active={page === 'home'} onClick={() => setPageAndClose('home')} />
        <NavButton icon={<WandSparkles size={18} />} label={t(language, 'investigate')} active={page === 'investigate'} onClick={() => setPageAndClose('investigate')} />
        <NavButton icon={<HistoryIcon size={18} />} label={t(language, 'history')} active={page === 'history'} onClick={() => setPageAndClose('history')} />
        <NavButton icon={<BarChart3 size={18} />} label={t(language, 'analytics')} active={page === 'analytics'} onClick={() => setPageAndClose('analytics')} />
        <div className="side-section-label">PRODUCT</div>
        <NavButton icon={<Sparkles size={18} />} label={t(language, 'how')} active={page === 'how'} onClick={() => setPageAndClose('how')} />
        <NavButton icon={<LayoutDashboard size={18} />} label={t(language, 'architecture')} active={page === 'architecture'} onClick={() => setPageAndClose('architecture')} />
        <NavButton icon={<Bell size={18} />} label={t(language, 'notifications')} badge={notifications.filter(n => !n.read).length} active={page === 'notifications'} onClick={() => setPageAndClose('notifications')} />
        <div className="side-spacer" />
        <NavButton icon={<User size={18} />} label={t(language, 'profile')} active={page === 'profile'} onClick={() => setPageAndClose('profile')} />
        <NavButton icon={<Settings size={18} />} label={t(language, 'settings')} active={page === 'settings'} onClick={() => setPageAndClose('settings')} />
        <button className="side-logout" onClick={logout}><LogOut size={17} /> {t(language, 'logout')}</button>
        <div className="profile-mini"><div className="avatar">{(profile.name || 'G').slice(0,1).toUpperCase()}</div><div><strong>{profile.name || 'Guest'}</strong><span>{isGuest ? 'Guest mode' : profile.email}</span></div></div>
      </aside>

      <main className="main-shell">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setMobileNav(v => !v)}><Menu size={21} /></button>
          <div className="breadcrumb"><span>BhashaLife</span><ArrowRight size={14} /><strong>{pageTitle(page, language)}</strong></div>
          <div className="top-actions">
            <button className="icon-button" title="Notifications" onClick={() => setPage('notifications')}><Bell size={18} />{notifications.some(n => !n.read) && <i />}</button>
            <div className="top-language">
              <button className="language-button" onClick={() => setShowLanguageMenu(v => !v)}><Globe size={16} />{language}<ChevronDown size={14} /></button>
              {showLanguageMenu && <LanguageMenu value={language} onChange={selectLanguage} />}
            </div>
          </div>
        </header>

        {page === 'home' && <Dashboard profile={profile} history={history} language={language} onNew={newInvestigation} onContinue={() => setPage('investigate')} onOpenHistory={() => setPage('history')} />}
        {page === 'investigate' && <InvestigationView language={language} uiLanguage={uiLanguage} report={report} messages={messages} loading={loading} message={message} setMessage={setMessage} selectedFile={selectedFile} inputMode={inputMode} activeTab={activeTab} setActiveTab={setActiveTab} showInputMenu={showInputMenu} setShowInputMenu={setShowInputMenu} openFilePicker={openFilePicker} openScreenshotPicker={openScreenshotPicker} selectLinkMode={selectLinkMode} selectTextMode={selectTextMode} fileInputRef={fileInputRef} screenshotInputRef={screenshotInputRef} handleFileChange={handleFileChange} handleScreenshotChange={handleScreenshotChange} analyze={analyze} useQuickAction={useQuickAction} startVoice={startVoice} voiceListening={voiceListening} voiceError={voiceError} speak={speak} newInvestigation={newInvestigation} profile={profile} />}
        {page === 'history' && <HistoryPage items={filteredHistory} search={searchHistory} setSearch={setSearchHistory} onNew={newInvestigation} />}
        {page === 'analytics' && <AnalyticsPage history={history} />}
        {page === 'how' && <HowPage language={language} onInvestigate={() => setPage('investigate')} />}
        {page === 'architecture' && <ArchitecturePage />}
        {page === 'notifications' && <NotificationsPage items={notifications} setItems={setNotifications} />}
        {page === 'profile' && <ProfilePage profile={profile} setProfile={setProfile} language={language} />}
        {page === 'settings' && <SettingsPage profile={profile} setProfile={setProfile} language={language} setLanguage={selectLanguage} logout={logout} setHistory={setHistory} />}
      </main>

      {showAuth && <AuthModal mode={authMode} setMode={setAuthMode} name={authName} setName={setAuthName} email={authEmail} setEmail={setAuthEmail} password={authPassword} setPassword={setAuthPassword} error={authError} onSubmit={handleAuth} onClose={() => setShowAuth(false)} />}
    </div>
  );
}

function NavButton({ icon, label, active, onClick, badge }: { icon: React.ReactNode; label: string; active?: boolean; onClick: () => void; badge?: number }) {
  return <button className={`nav-item ${active ? 'active' : ''}`} onClick={onClick}><span>{icon}</span><b>{label}</b>{badge ? <em>{badge}</em> : null}</button>;
}

function LanguageMenu({ value, onChange }: { value: Language; onChange: (value: Language) => void }) {
  return <div className="language-popover">{LANGS.map(item => <button key={item} onClick={() => onChange(item)}>{item}{item === value && <Check size={15} />}</button>)}</div>;
}

function LandingPage({ onStart, onGuest, onLogin }: { onStart: () => void; onGuest: () => void; onLogin: () => void }) {
  useReveal();
  const [menu, setMenu] = useState(false);
  const go = (id: string) => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  return <div className="landing">
    <nav className="landing-nav"><div className="landing-brand"><div className="brand-mark"><Shield size={22} /></div><strong>BhashaLife <span>AI</span></strong></div><div className="landing-links"><button onClick={() => go('solution')}>Solution</button><button onClick={() => go('intelligence')}>Intelligence</button><button onClick={() => go('workflow')}>How it works</button></div><div className="landing-actions"><button className="ghost-btn" onClick={onLogin}>Log in</button><button className="primary-btn small" onClick={onStart}>Get started <ArrowRight size={16} /></button><button className="mobile-menu" onClick={() => setMenu(v => !v)}><Menu size={20} /></button></div>{menu && <div className="mobile-landing-menu"><button onClick={() => go('solution')}>Solution</button><button onClick={() => go('intelligence')}>Intelligence</button><button onClick={() => go('workflow')}>How it works</button></div>}</nav>
    <section className="hero" data-reveal><div className="hero-grid" /><div className="hero-copy"><div className="hero-kicker"><span className="pulse-dot" /> Multilingual life & digital safety agent</div><h1>Understand what matters.<br /><span>Know what to do next.</span></h1><p>BhashaLife turns confusing notices, messages, screenshots and digital situations into clear, language-aware decisions and actionable next steps.</p><div className="hero-actions"><button className="primary-btn" onClick={onStart}>Start with BhashaLife <ArrowRight size={18} /></button><button className="secondary-btn" onClick={() => go('workflow')}><Play size={17} /> See how it works</button></div><div className="hero-trust"><span>English</span><span>हिंदी</span><span>मराठी</span><span>Hinglish</span><span>Roman input</span></div></div><div className="hero-visual"><div className="orbital orbital-a" /><div className="orbital orbital-b" /><div className="hero-card glass"><div className="mini-top"><span><Shield size={15} /> Live Intelligence</span><i>READY</i></div><div className="hero-risk"><div><small>Life Shield</small><strong>72</strong><span>HIGH RISK</span></div><div className="risk-ring"><span>72</span></div></div><div className="mini-line"><CheckCircle2 size={15} /> OTP exposure detected</div><div className="mini-line"><CheckCircle2 size={15} /> Trusted-channel verification</div><div className="mini-action">NEXT ACTION <strong>Secure your account</strong><ArrowRight size={15} /></div></div></div></section>
    <section className="clarity-section story-section landing-circuit circuit-clarity" data-reveal><div className="section-heading"><span>FROM CONFUSION TO CLARITY</span><h2>One situation. Four intelligent moves.</h2><p>You do not need to know which tool to use. BhashaLife works from the information you have and brings the next useful decision forward.</p></div><div className="clarity-track"><article className="clarity-card reveal-item" data-reveal><div className="clarity-number">01</div><div className="clarity-icon"><Languages size={22}/></div><span>YOU SHARE</span><h3>A notice, message, screenshot or link.</h3><p>Start with whatever you already have.</p><div className="clarity-signal"><i/><b>INPUT</b></div></article><ArrowRight className="clarity-arrow"/><article className="clarity-card reveal-item" data-reveal><div className="clarity-number">02</div><div className="clarity-icon"><Shield size={22}/></div><span>BHASHA SHIELD</span><h3>Language, script, meaning and intent.</h3><p>Understand it in the language you are comfortable with.</p><div className="clarity-signal"><i/><b>UNDERSTAND</b></div></article><ArrowRight className="clarity-arrow"/><article className="clarity-card reveal-item" data-reveal><div className="clarity-number">03</div><div className="clarity-icon"><Activity size={22}/></div><span>LIFE SHIELD</span><h3>Risk, consequences and what matters.</h3><p>Separate the signal from the noise.</p><div className="clarity-signal"><i/><b>PROTECT</b></div></article><ArrowRight className="clarity-arrow"/><article className="clarity-card reveal-item" data-reveal><div className="clarity-number">04</div><div className="clarity-icon"><ArrowRight size={22}/></div><span>NEXT ACTION</span><h3>One clear, practical move.</h3><p>Know what to do next — and adapt when things change.</p><div className="clarity-signal"><i/><b>ACT</b></div></article></div></section>
    <section id="solution" className="story-section landing-circuit circuit-solution" data-reveal><div className="section-heading"><span>01 — THE PROBLEM</span><h2>When information is clear, action becomes easier.</h2><p>People do not always need more information. They need the right meaning, the right risk context, and one clear next step.</p></div><div className="feature-grid"><FeatureCard icon={<Languages/>} title="Bhasha Shield" text="Understands language, script, transliteration and code-mixed input so users can stay in their comfortable language." /><FeatureCard icon={<Shield/>} title="Life Shield" text="Turns confusing signals into an application-level risk score, consequences and protective actions." /><FeatureCard icon={<WandSparkles/>} title="Agentic resolution" text="The system observes, chooses tools, evaluates the result and replans when new information changes the situation." /></div></section>
    <section id="intelligence" className="story-section dark-section landing-circuit circuit-intelligence" data-reveal><div className="section-heading"><span>02 — INTELLIGENCE</span><h2>One workspace. Many ways to understand.</h2><p>Upload a document, paste a link, share a screenshot or simply speak. BhashaLife brings the useful part forward.</p></div><div className="intelligence-board"><div className="board-chat"><div className="board-label">CONVERSATION</div><div className="fake-user">“Mala bonafide certificate nahiye. Ata kay karu?”</div><div className="fake-ai"><Shield size={16}/><div><strong>BhashaLife</strong><p>Bonafide certificate is required. Let's check the safest next option before the deadline.</p></div></div><div className="fake-composer"><Plus size={17}/><span>Ask in your language...</span><Mic size={17}/><ArrowUp size={17}/></div></div><div className="board-report"><div className="board-label">LIVE INTELLIGENCE</div><div className="report-mini-card"><span>RISK</span><strong>LOW · 12</strong></div><div className="report-mini-card important-mini"><span>IMPORTANT ONLY</span><strong>Deadline · Required docs · Next action</strong></div><div className="report-mini-card"><span>AGENT ACTIVITY</span><strong>Observe → Decide → Act → Adapt</strong></div></div></div></section>
    <section id="workflow" className="story-section landing-circuit circuit-workflow" data-reveal><div className="section-heading"><span>03 — THE AGENT LOOP</span><h2>It doesn't stop at an answer.</h2><p>New information can change the right action. BhashaLife keeps the investigation state and adapts the plan instead of starting over blindly.</p></div><div className="workflow-line">{['OBSERVE','DECIDE','ACT','EVALUATE','ADAPT'].map((x,i)=><React.Fragment key={x}><div className="workflow-step reveal-item" data-reveal><span>0{i+1}</span><strong>{x}</strong><small>{['Understand the input','Choose the right path','Use tools and evidence','Check the outcome','Replan if needed'][i]}</small></div>{i<4 && <ArrowRight className="workflow-arrow"/>}</React.Fragment>)}</div></section>
    <section className="cta-section" data-reveal><div><span>READY WHEN YOU ARE</span><h2>Confusing doesn't have to stay confusing.</h2><p>Start with the language you are comfortable with. BhashaLife will help you find the next move.</p></div><div className="cta-actions"><button className="primary-btn" onClick={onStart}>Get started <ArrowRight size={18}/></button><button className="text-btn" onClick={onGuest}>Try as guest</button></div></section>
    <footer className="landing-footer"><div><div className="landing-brand"><div className="brand-mark"><Shield size={18}/></div><strong>BhashaLife <span>AI</span></strong></div><p>Understand what matters. Know what to do next.</p></div><span>Built for multilingual, agentic problem solving.</span></footer>
  </div>;
}

function FeatureCard({ icon, title, text }: { icon: React.ReactNode; title: string; text: string }) { return <article className="feature-card reveal-item" data-reveal><div className="feature-icon">{icon}</div><h3>{title}</h3><p>{text}</p><ArrowRight size={17}/></article>; }

function Dashboard({ profile, history, language, onNew, onContinue, onOpenHistory }: { profile: UserProfile; history: HistoryItem[]; language: Language; onNew: () => void; onContinue: () => void; onOpenHistory: () => void }) {
  const high = history.filter(h => ['HIGH','CRITICAL'].includes(h.risk)).length;
  const pending = history.filter(h => h.status !== 'Resolved').length;
  return <div className="page-content"><div className="page-hero"><div><div className="eyebrow"><Sparkles size={15}/> PERSONAL INTELLIGENCE</div><h1>{profile.name ? `Good to see you, ${profile.name.split(' ')[0]}.` : 'Welcome to BhashaLife.'}</h1><p>Your investigations, risks and next actions in one calm workspace.</p></div><button className="primary-btn" onClick={onNew}><Plus size={18}/> Start new investigation</button></div><div className="attention-card"><div className="attention-icon"><Zap size={20}/></div><div><span>NEEDS YOUR ATTENTION</span><h3>{history[0]?.summary || 'No pending investigation yet'}</h3><p>{history[0] ? `${history[0].risk} risk · ${history[0].language} · ${history[0].date}` : 'Start by uploading a notice, message or screenshot.'}</p></div><button className="inline-action" onClick={history[0] ? onContinue : onNew}>Continue <ArrowRight size={16}/></button></div><div className="stats-grid"><Stat label="Investigations" value={String(history.length)} /><Stat label="Pending" value={String(pending)} /><Stat label="High / Critical" value={String(high)} /><Stat label="Languages" value={String(new Set(history.map(h => h.language)).size || 0)} /></div><div className="dashboard-grid"><section className="panel-card"><div className="panel-title"><div><span>RECENT INVESTIGATIONS</span><h2>Keep moving</h2></div><button className="text-btn" onClick={onOpenHistory}>View history <ArrowRight size={15}/></button></div>{history.length === 0 ? <EmptyState icon={<HistoryIcon/>} title="Your investigation history is empty" text="Start your first investigation and it will appear here." /> : history.slice(0,4).map(item => <HistoryRow key={item.id} item={item}/>)}</section><section className="panel-card"><div className="panel-title"><div><span>YOUR LANGUAGE</span><h2>{language === 'Auto' ? 'Auto detect' : language}</h2></div><Languages size={20}/></div><div className="language-insight"><div className="lang-ring">{language === 'Marathi' ? 'म' : language === 'Hindi' ? 'ह' : 'A'}</div><div><strong>Comfort-first interaction</strong><p>BhashaLife keeps system guidance aligned with your selected language and script.</p></div></div><div className="mini-checks"><span><Check size={14}/> Conversation</span><span><Check size={14}/> Live Intelligence</span><span><Check size={14}/> Action plan</span></div></section></div></div>;
}
function Stat({ label, value }: { label: string; value: string }) { return <div className="stat-card"><span>{label}</span><strong>{value}</strong></div>; }
function HistoryRow({ item }: { item: HistoryItem }) { return <div className="history-row"><div className="history-dot"/><div><strong>{item.summary}</strong><span>{item.date} · {item.language}</span></div><b className={`risk-pill ${item.risk.toLowerCase()}`}>{item.risk}</b></div>; }
function EmptyState({ icon, title, text }: { icon: React.ReactNode; title: string; text: string }) { return <div className="empty-state"><div>{icon}</div><h3>{title}</h3><p>{text}</p></div>; }



function InvestigationView(props: any) {
  const { language, uiLanguage, report, messages, loading, message, setMessage, selectedFile, inputMode, activeTab, setActiveTab, showInputMenu, setShowInputMenu, openFilePicker, openScreenshotPicker, selectLinkMode, selectTextMode, fileInputRef, screenshotInputRef, handleFileChange, handleScreenshotChange, analyze, useQuickAction, startVoice, voiceListening, voiceError, speak, newInvestigation, profile } = props;
  const important = report?.important_only || {};
  const activity = report?.agent_activity || [];
  const actionPlan = report?.action_plan || report?.what_to_do || [];
  const riskScore = report?.risk_score ?? null;
  const riskLevel = report?.risk_level || 'Unknown';
  const script = report?.script || detectScriptFor(uiLanguage, profile.script);
  const localized = (value: string | undefined) => value ? localizeGeneratedValue(value, uiLanguage, script) : '';
  const [copyState, setCopyState] = useState('');
  const reportText = () => buildReportText(report, uiLanguage, script);
  const handleCopyReport = async () => { if (!report) return; try { if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable'); await navigator.clipboard.writeText(reportText()); setCopyState(t(uiLanguage,'copied')); window.setTimeout(()=>setCopyState(''),1600); } catch { setCopyState(t(uiLanguage,'copyFailed')); } };
  const handleDownloadReport = () => { if (!report) return; const blob=new Blob([reportText()],{type:'text/plain;charset=utf-8'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download=`BhashaLife_Report_${new Date().toISOString().slice(0,10)}.txt`; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url); };
  return <div className="investigation-page"><div className="investigate-toolbar"><div><div className="eyebrow"><WandSparkles size={15}/> BHASHA SHIELD + LIFE SHIELD</div><h1>{t(uiLanguage,'workspaceTitle')}</h1><p>{t(uiLanguage, 'investigateDesc')}</p></div><div className="investigate-toolbar-actions">{report&&<><button className="secondary-btn compact-action" onClick={handleCopyReport}><Copy size={16}/> {t(uiLanguage,'copyReport')}</button><button className="secondary-btn compact-action" onClick={handleDownloadReport}><Download size={16}/> {t(uiLanguage,'exportReport')}</button></>}<button className="secondary-btn" onClick={newInvestigation}><Plus size={17}/> {t(uiLanguage,'newInvestigation')}</button></div></div><div className="investigate-grid"><section className="conversation-panel"><div className="conversation-head"><div><span>{t(uiLanguage,'conversation')}</span><strong>{language === 'Auto' ? t(uiLanguage,'autoLanguage') : language}</strong></div><div className="engine-ready"><i/>{loading ? t(uiLanguage,'analyzing') : t(uiLanguage,'engine')}</div></div><input ref={fileInputRef} type="file" hidden accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg,.webp" onChange={handleFileChange}/><input ref={screenshotInputRef} type="file" hidden accept="image/*" onChange={handleScreenshotChange}/><div className="conversation-scroll">{messages.length === 0 ? <div className="conversation-empty"><div className="empty-orb large"><Shield size={34}/></div><h2>{t(uiLanguage,'start')}</h2><p>{t(uiLanguage,'greeting')}</p><div className="quick-actions"><button onClick={() => useQuickAction(uiLanguage === 'Marathi' ? 'हे काय आहे?' : uiLanguage === 'Hindi' ? 'यह क्या है?' : 'What is this?')}>{uiLanguage==='Marathi'?'हे काय आहे?':uiLanguage==='Hindi'?'यह क्या है?':'What is this?'}</button><button onClick={() => useQuickAction(uiLanguage === 'Marathi' ? 'हे धोकादायक आहे का?' : uiLanguage === 'Hindi' ? 'क्या यह जोखिम भरा है?' : 'Is this risky?')}>{uiLanguage==='Marathi'?'हे धोकादायक आहे का?':uiLanguage==='Hindi'?'क्या यह जोखिम भरा है?':'Is this risky?'}</button><button onClick={() => useQuickAction(uiLanguage === 'Marathi' ? 'आता काय करावे?' : uiLanguage === 'Hindi' ? 'अब क्या करना चाहिए?' : 'What should I do?')}>{uiLanguage==='Marathi'?'आता काय करावे?':uiLanguage==='Hindi'?'अब क्या करना चाहिए?':'What should I do?'}</button></div></div> : messages.map((item: ChatMessage) => <div className={`chat-message ${item.role}`} key={item.id}><div className="chat-avatar">{item.role === 'assistant' ? <Shield size={16}/> : <span>{t(uiLanguage,'you')}</span>}</div><div className="chat-bubble"><div className="chat-name">{item.role === 'assistant' ? 'BhashaLife AI' : t(uiLanguage,'you')}</div><p>{item.role === 'assistant' ? localizeGeneratedValue(item.text, uiLanguage, script) : item.text}</p>{item.attachment && <div className="attachment-chip"><Paperclip size={13}/>{item.attachment}</div>}{item.role === 'assistant' && profile.tts && <button className="speak-button" onClick={() => speak(item.text)}><Volume2 size={14}/></button>}</div></div>)}{loading && <div className="chat-message assistant"><div className="chat-avatar"><Activity size={16}/></div><div className="chat-bubble loading-bubble"><div className="thinking-dots"><i/><i/><i/></div><strong>{t(uiLanguage,'analyzing')}</strong><span>{t(uiLanguage,'agentLoop')}</span></div></div>}</div><div className="composer-area"><div className="input-tools">{showInputMenu && <div className="input-menu"><button onClick={openFilePicker}><FileText/><span><b>{t(uiLanguage,'upload')}</b><small>{t(uiLanguage,'uploadDesc')}</small></span></button><button onClick={openScreenshotPicker}><ImageIcon/><span><b>{t(uiLanguage,'screenshot')}</b><small>{t(uiLanguage,'screenshotDesc')}</small></span></button><button onClick={selectLinkMode}><LinkIcon/><span><b>{t(uiLanguage,'link')}</b><small>{t(uiLanguage,'linkDesc')}</small></span></button><button onClick={selectTextMode}><FileText/><span><b>{t(uiLanguage,'text')}</b><small>{t(uiLanguage,'textDesc')}</small></span></button></div>}</div><div className="composer"><button className="composer-icon" onClick={() => setShowInputMenu((v: boolean) => !v)}><Plus/></button><input value={message} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMessage(e.target.value)} onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => { if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();analyze();}}} disabled={loading} placeholder={inputMode === 'link' ? t(uiLanguage,'linkPlaceholder') : selectedFile ? selectedFile.name : t(uiLanguage,'ask')}/><button className={`voice-button ${voiceListening?'listening':''}`} onClick={startVoice} title={voiceListening ? t(uiLanguage,'stopVoice') : t(uiLanguage,'voiceInput')}>{voiceListening?<Square size={16}/>:<Mic size={19}/>}</button><button className="send-button" onClick={analyze} disabled={loading || (!message.trim()&&!selectedFile)}>{loading?<Activity size={19}/>:<Send size={18}/>}</button></div>{voiceError&&<div className="voice-error">{voiceError}</div>}<small className="composer-note">{t(uiLanguage,'composerNote')}</small></div></section>
    <aside className="intelligence-panel"><div className="intelligence-head"><div><div className="report-title"><Activity size={17}/>{t(uiLanguage,'live')}</div><span>{t(uiLanguage,'decisionSupport')}</span></div><span className="live-badge"><i/>{t(uiLanguage,'liveBadge')}</span></div><div className="report-tabs">{(['Overview','Important','What To Do'] as const).map(tab=><button key={tab} className={activeTab===tab?'selected':''} onClick={() => setActiveTab(tab)}>{tab==='Overview'?t(uiLanguage,'overview'):tab==='Important'?t(uiLanguage,'important'):t(uiLanguage,'todo')}</button>)}</div>{report&&<div className="report-actions"><button onClick={handleCopyReport}><Copy size={14}/>{copyState||t(uiLanguage,'copyReport')}</button><button onClick={handleDownloadReport}><Download size={14}/>{t(uiLanguage,'downloadReport')}</button></div>}{!report?<div className="intelligence-empty"><div className="shield-pulse"><Shield size={29}/></div><h2>{t(uiLanguage,'waitingTitle')}</h2><p>{t(uiLanguage,'waitingText')}</p><div className="preview-stack"><div><span>{t(uiLanguage,'situation')}</span><b>—</b></div><div><span>{t(uiLanguage,'risk')}</span><b>—</b></div><div><span>{t(uiLanguage,'next')}</span><b>—</b></div></div></div>:<div className="intelligence-scroll">{activeTab==='Overview'&&<><div className="intel-card"><span className="card-label">{t(uiLanguage,'situation')}</span><h3>{localized(report.situation)||t(uiLanguage,'situationUnderstood')}</h3>{report.user_goal&&<p>{localized(report.user_goal)}</p>}</div><div className={`risk-card ${String(riskLevel).toLowerCase()}`}><div><span>{t(uiLanguage,'risk')}</span><strong>{riskScore ?? '—'}<small>/100</small></strong><b>{localizeRisk(riskLevel,uiLanguage)}</b></div><div className="risk-meter"><div style={{width:`${Math.max(0,Math.min(100,riskScore||0))}%`}}/></div><p>{(report.risk_factors||[]).slice(0,3).map((x:string)=>localized(x)).join(' · ')}</p></div><div className="next-card"><span>{t(uiLanguage,'next')}</span><strong>{localized(important.next_step || actionPlan[0] || t(uiLanguage,'reviewActionPlan'))}</strong><button onClick={() => setActiveTab('What To Do')}>{t(uiLanguage,'openActionPlan')} <ArrowRight size={15}/></button></div><div className="intel-card"><span className="card-label">{t(uiLanguage,'resolution')}</span><div className="readiness"><div className="readiness-track"><i style={{width:`${Math.round((report.confidence||0)*100)}%`}}/></div><strong>{Math.round((report.confidence||0)*100)}%</strong></div><p>{localizeGeneratedValue(report.evaluation_status,uiLanguage,report?.script||'Latin') || t(uiLanguage,'evaluationProgress')}</p></div><div className="intel-card"><div className="card-label">{t(uiLanguage,'activity')}</div><ActivityTimeline items={activity} language={uiLanguage}/></div></>}{activeTab==='Important'&&<ImportantPanel important={important} report={report} language={uiLanguage}/>} {activeTab==='What To Do'&&<ActionPanel report={report} language={uiLanguage}/>}</div>}</aside></div></div>;
}

function ActivityTimeline({ items, language }: { items: string[]; language: Language }) { return <div className="timeline">{items.slice(-8).map((item,i)=><div className="timeline-item" key={`${item}-${i}`}><span className="timeline-dot"><Check size={12}/></span><div><strong>{localizeGeneratedValue(item, language, language==='Marathi'?'Devanagari':'Latin')}</strong><small>{i===items.slice(-8).length-1?t(language,'latest'):t(language,'agentStep')}</small></div></div>)}</div>; }
function ImportantPanel({ important, report, language }: { important: ImportantOnly; report: ReportData; language: Language }) { const docs=important.required_documents||report.document_insights?.required_documents||[]; const script=report.script||detectScriptFor(language,'Auto'); return <div className="important-panel"><div className="important-hero"><Zap size={19}/><div><span>{t(language,'importantOnly')}</span><strong>{localizeGeneratedValue(important.action || report.document_insights?.action || t(language,'focusAction'), language, script)}</strong></div></div><InfoRow label={t(language,'deadline')} value={important.deadline || report.document_insights?.deadline} language={language} script={script}/><InfoList label={t(language,'required')} items={docs} language={language} script={script}/><InfoRow label={t(language,'consequence')} value={important.consequence || report.document_insights?.consequence} language={language} script={script}/><InfoRow label={t(language,'nextStep')} value={important.next_step || important.action || report.document_insights?.action} language={language} script={script}/></div>; }
function ActionPanel({ report, language }: { report: ReportData; language: Language }) { const actions=report.action_plan||report.what_to_do||[]; const avoid=report.what_not_to_do||[]; const script=report.script||detectScriptFor(language,'Auto'); return <div className="action-panel"><div className="action-heading"><span>{t(language,'actionPlan')}</span><h2>{t(language,'actionPlanTitle')}</h2></div><ol>{actions.map((a,i)=><li key={`${a}-${i}`}><span>{i+1}</span><p>{localizeGeneratedValue(a,language,script)}</p></li>)}</ol>{avoid.length>0&&<div className="avoid-box"><AlertTriangle size={17}/><div><strong>{t(language,'whatNotToDo')}</strong>{avoid.slice(0,4).map((a,i)=><p key={i}>{localizeGeneratedValue(a,language,script)}</p>)}</div></div>}</div>; }
function InfoRow({ label, value, language, script }: { label: string; value?: string; language:Language; script:string }) { return <div className="info-row"><span>{label}</span><strong>{value?localizeGeneratedValue(value,language,script):t(language,'noData')}</strong></div>; }
function InfoList({ label, items, language, script }: { label: string; items: string[]; language:Language; script:string }) { return <div className="info-list"><span>{label}</span>{items.length?items.map((x,i)=><strong key={i}><CheckCircle2 size={14}/>{localizeGeneratedValue(x,language,script)}</strong>):<strong>{t(language,'noneIdentified')}</strong>}</div>; }

function HistoryPage({ items, search, setSearch, onNew }: { items: HistoryItem[]; search: string; setSearch: (v:string)=>void; onNew:()=>void }) { return <div className="page-content"><div className="page-hero"><div><div className="eyebrow"><HistoryIcon size={15}/> MEMORY</div><h1>Investigation history</h1><p>Every investigation stays lightweight and easy to revisit.</p></div><button className="primary-btn" onClick={onNew}><Plus size={18}/> New investigation</button></div><div className="search-bar"><Search size={18}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search investigations..."/></div><div className="panel-card history-panel">{items.length===0?<EmptyState icon={<HistoryIcon/>} title="No investigations yet" text="Your next investigation will appear here."/>:items.map(item=><HistoryRow key={item.id} item={item}/>)}</div></div>; }
function AnalyticsPage({ history }: { history: HistoryItem[] }) { const risks=['LOW','MODERATE','HIGH','CRITICAL'].map(r=>({r,n:history.filter(h=>h.risk===r).length})); const resolved=history.filter(h=>h.status==='Resolved').length; const languages=Object.entries(history.reduce<Record<string,number>>((a,h)=>(a[h.language]=(a[h.language]||0)+1,a),{})); return <div className="page-content"><div className="page-hero"><div><div className="eyebrow"><BarChart3 size={15}/> SIGNALS & TRENDS</div><h1>Your intelligence overview</h1><p>Useful patterns from your local investigation history.</p></div></div><div className="stats-grid"><Stat label="Total" value={String(history.length)}/><Stat label="Resolved" value={String(resolved)}/><Stat label="Resolution rate" value={history.length?`${Math.round(resolved/history.length*100)}%`:'0%'}/><Stat label="High / Critical" value={String(history.filter(h=>['HIGH','CRITICAL'].includes(h.risk)).length)}/></div><div className="analytics-grid"><section className="panel-card"><div className="panel-title"><div><span>RISK DISTRIBUTION</span><h2>Life Shield signals</h2></div><Shield size={20}/></div>{risks.map(x=><div className="bar-row" key={x.r}><span>{x.r}</span><div><i style={{width:`${history.length?Math.max(4,x.n/history.length*100):4}%`}}/></div><b>{x.n}</b></div>)}</section><section className="panel-card"><div className="panel-title"><div><span>LANGUAGE USAGE</span><h2>Comfort patterns</h2></div><Languages size={20}/></div>{languages.length?languages.map(([lang,n])=><div className="language-row" key={lang}><span>{lang}</span><b>{n}</b></div>):<EmptyState icon={<Languages/>} title="No language data yet" text="Complete an investigation to see patterns."/>}</section></div></div>; }

function HowPage({ onInvestigate }: { language: Language; onInvestigate:()=>void }) { const steps=[['01','Understand','Bhasha Shield identifies language, script, intent and context.'],['02','Investigate','The orchestrator selects OCR, document, URL and retrieval tools as needed.'],['03','Protect','Life Shield assesses risk and surfaces consequences.'],['04','Act','The planner turns findings into a short, actionable plan.'],['05','Adapt','New information updates state, risk and the plan.']]; return <div className="page-content narrative"><div className="page-hero"><div><div className="eyebrow"><Sparkles size={15}/> HOW IT WORKS</div><h1>From confusion to a next action.</h1><p>A visible agent loop keeps the system understandable and accountable.</p></div><button className="primary-btn" onClick={onInvestigate}>Try an investigation <ArrowRight size={17}/></button></div><div className="steps-stack">{steps.map(([n,title,text])=><article className="step-card" key={n}><span>{n}</span><div><h2>{title}</h2><p>{text}</p></div><ArrowRight/></article>)}</div></div>; }
function ArchitecturePage() { const nodes=['User input','Bhasha Shield','Agent Orchestrator','OCR / Document / URL / RAG','Reasoning + Risk','Action Planner','Evaluator','Adaptive replan']; return <div className="page-content narrative"><div className="page-hero"><div><div className="eyebrow"><LayoutDashboard size={15}/> SYSTEM MAP</div><h1>Architecture built for action.</h1><p>Every stage has a job: understand, decide, act, evaluate and adapt.</p></div></div><div className="architecture-flow">{nodes.map((n,i)=><React.Fragment key={n}><div className="arch-node"><span>{String(i+1).padStart(2,'0')}</span><strong>{n}</strong></div>{i<nodes.length-1&&<ArrowDownSmall/>}</React.Fragment>)}</div></div>; }
function ArrowDownSmall(){ return <div className="arch-arrow">↓</div>; }
function NotificationsPage({ items, setItems }: { items: any[]; setItems: (v:any[])=>void }) { return <div className="page-content"><div className="page-hero"><div><div className="eyebrow"><Bell size={15}/> NOTIFICATION CENTER</div><h1>Stay ahead of what needs attention.</h1><p>Important changes from your investigations appear here.</p></div></div><div className="panel-card notification-panel">{items.length===0?<EmptyState icon={<Bell/>} title="You're all clear" text="New action or follow-up alerts will appear here."/>:items.map((n:any)=><div className={`notification-row ${n.read?'read':''}`} key={n.id}><div className="notification-icon"><Bell size={17}/></div><div><strong>{n.title}</strong><p>{n.body}</p><small>{n.type}</small></div><button className="text-btn" onClick={()=>setItems(items.map(x=>x.id===n.id?{...x,read:true}:x))}>{n.read?'Read':'Mark read'}</button></div>)}</div></div>; }
function ProfilePage({ profile, setProfile, language }: { profile:UserProfile; setProfile:React.Dispatch<React.SetStateAction<UserProfile>>; language:Language }) { return <div className="page-content"><div className="page-hero"><div><div className="eyebrow"><User size={15}/> YOUR PROFILE</div><h1>{profile.name||'Guest profile'}</h1><p>{profile.email||'Guest mode'} · Preferred interaction: {language}</p></div></div><div className="profile-grid"><section className="panel-card profile-card"><div className="big-avatar">{(profile.name||'G').slice(0,1).toUpperCase()}</div><label>Full name<input value={profile.name} onChange={e=>setProfile(p=>({...p,name:e.target.value}))}/></label><label>Email<input value={profile.email} onChange={e=>setProfile(p=>({...p,email:e.target.value}))}/></label></section><section className="panel-card"><div className="panel-title"><div><span>LANGUAGE & VOICE</span><h2>Comfort settings</h2></div><Languages size={20}/></div><p className="setting-note">Your language preference is shared with the investigation workspace.</p><div className="preference-card"><strong>Preferred language</strong><span>{language}</span></div><div className="preference-card"><strong>Script</strong><span>{profile.script}</span></div><div className="preference-card"><strong>Voice input</strong><span>{profile.voiceInput?'Enabled':'Disabled'}</span></div></section></div></div>; }
function SettingsPage({ profile, setProfile, language, setLanguage, logout, setHistory }: { profile:UserProfile; setProfile:React.Dispatch<React.SetStateAction<UserProfile>>; language:Language; setLanguage:(v:Language)=>void; logout:()=>void; setHistory:(v:HistoryItem[])=>void }) { const toggle=(key:keyof UserProfile)=>(e:React.ChangeEvent<HTMLInputElement>)=>setProfile(p=>({...p,[key]:e.target.checked})); return <div className="page-content"><div className="page-hero"><div><div className="eyebrow"><Settings size={15}/> CONTROL CENTER</div><h1>Settings</h1><p>Make BhashaLife work the way you naturally interact.</p></div></div><div className="settings-list"><SettingSelect label="Interface language" value={language} options={LANGS} onChange={setLanguage}/><SettingSelect label="Script preference" value={profile.script} options={['Auto','Devanagari','Latin'] as any} onChange={(v:any)=>setProfile(p=>({...p,script:v}))}/><Toggle label="Voice input" description="Use your browser microphone to dictate into the investigation." checked={profile.voiceInput} onChange={toggle('voiceInput')}/><Toggle label="Text to speech" description="Show a speaker action on assistant responses. Autoplay stays off." checked={profile.tts} onChange={toggle('tts')}/><Toggle label="Larger text" description="Increase reading sizes across the platform." checked={profile.largeText} onChange={toggle('largeText')}/><Toggle label="High contrast" description="Increase contrast for important interface elements." checked={profile.highContrast} onChange={toggle('highContrast')}/><Toggle label="Reduce motion" description="Respect reduced-motion preferences and simplify animations." checked={profile.reducedMotion} onChange={toggle('reducedMotion')}/><Toggle label="Notifications" description="Allow local action and adaptation alerts." checked={profile.notifications} onChange={toggle('notifications')}/><div className="danger-zone"><div><strong>Clear local history</strong><p>Remove investigation metadata stored in this browser.</p></div><button className="danger-btn" onClick={()=>setHistory([])}>Clear history</button></div><div className="danger-zone"><div><strong>Sign out</strong><p>Return to the BhashaLife landing page.</p></div><button className="danger-btn" onClick={logout}>Logout</button></div></div></div>; }
function SettingSelect({ label, value, options, onChange }: { label:string; value:any; options:any[]; onChange:(v:any)=>void }) { return <div className="setting-row"><div><strong>{label}</strong><p>Choose the experience you prefer.</p></div><select value={value} onChange={e=>onChange(e.target.value)}>{options.map(o=><option key={o}>{o}</option>)}</select></div>; }
function Toggle({ label, description, checked, onChange }: { label:string; description:string; checked:boolean; onChange:(e:React.ChangeEvent<HTMLInputElement>)=>void }) { return <label className="setting-row toggle-row"><div><strong>{label}</strong><p>{description}</p></div><span className={`switch ${checked?'on':''}`}><input type="checkbox" checked={checked} onChange={onChange}/><i/></span></label>; }
function AuthModal({ mode, setMode, name, setName, email, setEmail, password, setPassword, error, onSubmit, onClose }: { mode:'login'|'signup'; setMode:(m:'login'|'signup')=>void; name:string; setName:(v:string)=>void; email:string; setEmail:(v:string)=>void; password:string; setPassword:(v:string)=>void; error:string; onSubmit:(e:React.FormEvent)=>void; onClose:()=>void }) { return <div className="modal-backdrop"><div className="auth-modal"><button className="modal-close" onClick={onClose}><X/></button><div className="auth-brand"><div className="brand-mark"><Shield size={21}/></div><div><strong>BhashaLife <span>AI</span></strong><small>Private demo workspace</small></div></div><div className="auth-tabs"><button className={mode==='login'?'active':''} onClick={()=>setMode('login')}>Log in</button><button className={mode==='signup'?'active':''} onClick={()=>setMode('signup')}>Sign up</button></div><h2>{mode==='login'?'Welcome back.':'Create your workspace.'}</h2><p>{mode==='login'?'Continue your investigations with your saved local preferences.':'Create a demo account with your email and password.'}</p><form onSubmit={onSubmit}>{mode==='signup'&&<label>Full name<input value={name} onChange={e=>setName(e.target.value)} placeholder="Your name"/></label>}<label>Email<input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com"/></label><label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="At least 6 characters" minLength={6}/></label>{error&&<div className="auth-error">{error}</div>}<button className="primary-btn full" type="submit">{mode==='login'?'Log in':'Create account'} <ArrowRight size={17}/></button></form><button className="auth-switch" onClick={()=>setMode(mode==='login'?'signup':'login')}>{mode==='login'?"Don't have an account? Sign up":"Already have an account? Log in"}</button><small className="demo-disclaimer">Demo authentication is stored locally in this browser and is not production-secure.</small></div></div>; }

function pageTitle(page: Page, language: Language) { const map:Record<Page,string>={home:t(language,'home'),investigate:t(language,'investigate'),history:t(language,'history'),analytics:t(language,'analytics'),how:t(language,'how'),architecture:t(language,'architecture'),notifications:t(language,'notifications'),profile:t(language,'profile'),settings:t(language,'settings')}; return map[page]; }
function localizeRisk(level:string,language:Language){const m:any={LOW:{Hindi:'कम',Marathi:'कमी','Hinglish / Roman':'LOW'},MODERATE:{Hindi:'मध्यम',Marathi:'मध्यम','Hinglish / Roman':'MODERATE'},HIGH:{Hindi:'उच्च',Marathi:'उच्च','Hinglish / Roman':'HIGH'},CRITICAL:{Hindi:'गंभीर',Marathi:'गंभीर','Hinglish / Roman':'CRITICAL'},Unknown:{Hindi:'अज्ञात',Marathi:'अज्ञात','Hinglish / Roman':'Unknown'}};return m[level]?.[language]||level;}
function localizeStatic(text:string,language:string){if(language==='Hindi')return 'मैं BhashaLife इंजन से कनेक्ट नहीं कर पाया। कृपया सुनिश्चित करें कि FastAPI बैकएंड पोर्ट 8001 पर चल रहा है।';if(language==='Marathi')return 'मी BhashaLife इंजिनशी कनेक्ट करू शकलो नाही. कृपया FastAPI बॅकएंड पोर्ट 8001 वर चालू आहे याची खात्री करा.';if(language==='Hinglish / Roman')return 'BhashaLife engine se connect nahi ho paya. Please check karo ki FastAPI backend port 8001 par run ho raha hai.';return text;}
function localizeCommonTerms(text:string|undefined,language:string,script:string){if(!text||language==='English'||language==='Auto')return text||'';const d:Record<string,Record<string,string>>={Hindi:{'understanding user input':'यूज़र इनपुट समझा जा रहा है','language detected':'भाषा पहचानी गई','new information received':'नई जानकारी मिली','previous agent state retrieved':'पिछली एजेंट स्थिति प्राप्त हुई','follow-up request detected':'फॉलो-अप अनुरोध पहचाना गया','preserving previous situation and goal':'पिछली स्थिति और लक्ष्य सुरक्षित रखे गए','risk reassessed':'जोखिम का दोबारा आकलन किया गया','goal updated':'लक्ष्य अपडेट किया गया','replanning actions':'कार्रवाइयों की नई योजना बनाई जा रही है','new action plan generated':'नई कार्य योजना तैयार हुई','analysis complete':'विश्लेषण पूरा हुआ','potential threatening communication':'संभावित धमकी वाला संदेश','potential phishing or financial safety situation':'संभावित फिशिंग या वित्तीय सुरक्षा स्थिति','secure affected account':'प्रभावित खाते को सुरक्षित करें','stop risky action and secure the situation immediately':'जोखिम वाली कार्रवाई रोकें और स्थिति को तुरंत सुरक्षित करें','verify through a trusted channel':'विश्वसनीय माध्यम से सत्यापित करें','review the information and complete the relevant next step':'जानकारी की समीक्षा करें और अगला जरूरी कदम पूरा करें','do not share otp':'OTP साझा न करें','do not share passwords':'पासवर्ड साझा न करें','do not click suspicious links':'संदिग्ध लिंक पर क्लिक न करें'},Marathi:{'understanding user input':'वापरकर्त्याचा इनपुट समजून घेत आहे','language detected':'भाषा ओळखली गेली','new information received':'नवीन माहिती मिळाली','previous agent state retrieved':'मागील एजंट स्थिती मिळवली','follow-up request detected':'फॉलो-अप विनंती ओळखली','preserving previous situation and goal':'मागील परिस्थिती आणि उद्दिष्ट जतन केले','risk reassessed':'धोक्याचे पुन्हा मूल्यांकन केले','goal updated':'उद्दिष्ट अपडेट केले','replanning actions':'कृतींचे पुनर्नियोजन केले','new action plan generated':'नवीन कृती योजना तयार केली','analysis complete':'विश्लेषण पूर्ण झाले','potential threatening communication':'संभाव्य धमकीचा संदेश','potential phishing or financial safety situation':'संभाव्य फिशिंग किंवा आर्थिक सुरक्षा परिस्थिती','secure affected account':'प्रभावित खाते सुरक्षित करा','stop risky action and secure the situation immediately':'धोकादायक कृती थांबवा आणि परिस्थिती त्वरित सुरक्षित करा','verify through a trusted channel':'विश्वसनीय माध्यमातून पडताळणी करा','review the information and complete the relevant next step':'माहिती तपासा आणि संबंधित पुढील कृती पूर्ण करा','do not share otp':'OTP शेअर करू नका','do not share passwords':'पासवर्ड शेअर करू नका','do not click suspicious links':'संशयास्पद लिंकवर क्लिक करू नका'},'Hinglish / Roman':{'understanding user input':'User input samjha ja raha hai','language detected':'Language detect hui','new information received':'Nayi information mili','previous agent state retrieved':'Previous agent state mila','follow-up request detected':'Follow-up request detect hui','preserving previous situation and goal':'Previous situation aur goal preserve kiya gaya','risk reassessed':'Risk dobara assess kiya gaya','goal updated':'Goal update hua','replanning actions':'Actions ko replan kiya ja raha hai','new action plan generated':'Naya action plan generate hua','analysis complete':'Analysis complete hua','potential threatening communication':'Possible threatening message','potential phishing or financial safety situation':'Possible phishing ya financial safety situation','secure affected account':'Affected account ko secure karein','stop risky action and secure the situation immediately':'Risky action rokein aur situation ko immediately secure karein','verify through a trusted channel':'Trusted channel se verify karein','review the information and complete the relevant next step':'Information review karke relevant next step complete karein','do not share otp':'OTP share na karein','do not share passwords':'Password share na karein','do not click suspicious links':'Suspicious link par click na karein'}};let result=text;Object.entries(d[language]||{}).sort(([a],[b])=>b.length-a.length).forEach(([from,to])=>{result=result.replace(new RegExp(from.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi'),to)});if(language==='Marathi'&&script==='Latin'){const r:Record<string,string>={'भाषा ओळखली गेली':'Bhasha olakhli geli','नवीन माहिती मिळाली':'Navin mahiti milali','मागील एजंट स्थिती मिळवली':'Magil agent sthiti milali','धोक्याचे पुन्हा मूल्यांकन केले':'Dhokyache punha mulyankan kele','उद्दिष्ट अपडेट केले':'Uddisht update kele','नवीन कृती योजना तयार केली':'Navin kruti yojana tayar keli','विश्लेषण पूर्ण झाले':'Vishleshan purna zale'};Object.entries(r).forEach(([a,b])=>{result=result.split(a).join(b)})}return result;}

const generatedPhraseMaps:Record<string,Record<string,string>>={
Hindi:{'verify the request through the institution\'s official channel':'संस्था के आधिकारिक माध्यम से अनुरोध सत्यापित करें','retrieving trusted safety knowledge':'विश्वसनीय सुरक्षा जानकारी प्राप्त की जा रही है','document analysis complete':'दस्तावेज़ विश्लेषण पूरा हुआ','review the recommended action plan':'सुझाई गई कार्य योजना देखें','review the information':'जानकारी की समीक्षा करें','complete the relevant next step':'ज़रूरी अगला कदम पूरा करें','no immediate safety risk detected':'कोई तत्काल सुरक्षा जोखिम नहीं मिला','missing requirement':'ज़रूरी दस्तावेज़ उपलब्ध नहीं है','required document':'ज़रूरी दस्तावेज़'},
Marathi:{'verify the request through the institution\'s official channel':'संस्थेच्या अधिकृत माध्यमातून विनंती पडताळा','retrieving trusted safety knowledge':'विश्वसनीय सुरक्षा माहिती मिळवत आहे','document analysis complete':'दस्तऐवज विश्लेषण पूर्ण झाले','review the recommended action plan':'सुचवलेली कृती योजना पहा','review the information':'माहिती तपासा','complete the relevant next step':'संबंधित पुढील कृती पूर्ण करा','no immediate safety risk detected':'तात्काळ सुरक्षा धोका आढळला नाही','missing requirement':'आवश्यक कागदपत्र उपलब्ध नाही','required document':'आवश्यक कागदपत्र'},
'Hinglish / Roman':{'verify the request through the institution\'s official channel':'Institution ke official channel se request verify karein','retrieving trusted safety knowledge':'Trusted safety knowledge retrieve ho raha hai','document analysis complete':'Document analysis complete hua','review the recommended action plan':'Recommended action plan dekho','review the information':'Information review karo','complete the relevant next step':'Relevant next step complete karo','no immediate safety risk detected':'Koi immediate safety risk detect nahi hua','missing requirement':'Required document available nahi hai','required document':'Required document'}};
function localizeGeneratedValue(
  value: string | undefined,
  language: string,
  script: string
) {
  if (!value) return '';

  if (language === 'English' || language === 'Auto') {
    return value;
  }

  let result = localizeCommonTerms(
    value,
    language,
    script
  );

  const generatedMap =
    generatedPhraseMaps[language] || {};

  const escapeRegExp = (text: string) =>
    text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  Object.entries(generatedMap)
    .sort(([a], [b]) => b.length - a.length)
    .forEach(([from, to]) => {
      result = result.replace(
        new RegExp(escapeRegExp(from), 'gi'),
        to
      );
    });

  const documentTerms: Record<
    string,
    Record<string, string>
  > = {
    Hindi: {
      'bonafide certificate': 'बोनाफाइड प्रमाणपत्र',
      'college id': 'कॉलेज आईडी',
      'student id': 'छात्र आईडी',
      'student id card': 'छात्र पहचान पत्र',
      photograph: 'फोटो',
    },

    Marathi: {
      'bonafide certificate': 'बोनाफाइड प्रमाणपत्र',
      'college id': 'कॉलेज आयडी',
      'student id': 'विद्यार्थी ओळखपत्र',
      'student id card': 'विद्यार्थी ओळखपत्र',
      photograph: 'फोटो',
    },

    'Hinglish / Roman': {
      'bonafide certificate': 'bonafide certificate',
      'college id': 'college ID',
      'student id': 'student ID',
      'student id card': 'student ID card',
      photograph: 'photo',
    },
  };

  const languageTerms =
    documentTerms[language] || {};

  Object.entries(languageTerms)
    .sort(([a], [b]) => b.length - a.length)
    .forEach(([from, to]) => {
      result = result.replace(
        new RegExp(escapeRegExp(from), 'gi'),
        to
      );
    });

  return result;
}

function localizeRiskLevel(level:string|undefined,language:Language){if(!level)return t(language,'noData');if(language==='Hindi')return ({LOW:'कम',MODERATE:'मध्यम',HIGH:'उच्च',CRITICAL:'गंभीर'} as Record<string,string>)[level]||level;if(language==='Marathi')return ({LOW:'कमी',MODERATE:'मध्यम',HIGH:'उच्च',CRITICAL:'गंभीर'} as Record<string,string>)[level]||level;return level;}
function buildReportText(report:ReportData,language:Language,script:string){const L=(v?:string)=>localizeGeneratedValue(v,language,script);const imp=report.important_only||{};const actions=report.action_plan||report.what_to_do||[];const avoid=report.what_not_to_do||[];const activity=report.agent_activity||[];const lines=[t(language,'reportTitle'),'','— '+t(language,'situation')+' —',L(report.situation)||t(language,'situationUnderstood'),'','— '+t(language,'risk')+' —',`${report.risk_score??'—'}/100 · ${localizeRiskLevel(report.risk_level,language)}`];if(report.risk_factors?.length)lines.push(...report.risk_factors.map(x=>'• '+L(x)));lines.push('','— '+t(language,'importantOnly')+' —',`${t(language,'deadline')}: ${L(imp.deadline||report.document_insights?.deadline)||t(language,'noData')}`,`${t(language,'required')}: ${(imp.required_documents||report.document_insights?.required_documents||[]).map(x=>L(x)).join(', ')||t(language,'noneIdentified')}`,`${t(language,'consequence')}: ${L(imp.consequence||report.document_insights?.consequence)||t(language,'noData')}`,`${t(language,'nextStep')}: ${L(imp.next_step||actions[0])||t(language,'noData')}`,'','— '+t(language,'actionPlan')+' —',...actions.map((x,i)=>`${i+1}. ${L(x)}`));if(avoid.length)lines.push('',`— ${t(language,'whatNotToDo')} —`,...avoid.map(x=>'• '+L(x)));if(activity.length)lines.push('',`— ${t(language,'activity')} —`,...activity.map(x=>'✓ '+L(x)));lines.push('',`${t(language,'confidence')}: ${Math.round((report.confidence||0)*100)}%`);return lines.join('\n');}

function buildAssistantResponse(data:ReportData){const language=data.language||'English';const script=data.script==='Latin'?'Latin':'Devanagari';const missing=data.important_only?.missing_requirement||data.document_insights?.missing_requirement;const next=data.important_only?.next_step||data.document_insights?.action_plan?.[0]||data.action_plan?.[0];const deadline=data.important_only?.deadline||data.document_insights?.deadline;const high=data.risk_level==='CRITICAL'||data.risk_level==='HIGH';const L=(v?:string)=>localizeGeneratedValue(v,language,script);const m=L(missing),n=L(next),d=L(deadline);if(language==='Marathi'&&script==='Latin')return m?`Tumchya arjasaathi ${m} avashyak aahe ani te uplabdh nahi.${n?` Pudhil kruti: ${n}.`:''}${d?` ${d} purvi purna kara.`:''}`:high?'Hi paristhiti dhokadayak asu shakate. Risky kruti thambva ani Live Intelligence madhil suraksha suchana pala.':n?`Mi paristhitiche vishleshan kele aahe. Pudhil kruti: ${n}.`:'Mi paristhitiche vishleshan kele aahe. Live Intelligence madhil pudhil kruti paha.';if(language==='Marathi')return m?`तुमच्या अर्जासाठी ${m} आवश्यक आहे आणि ते उपलब्ध नाही.${n?` पुढील कृती: ${n}.`:''}${d?` ${d} पूर्वी पूर्ण करा.`:''}`:high?'ही परिस्थिती धोकादायक असू शकते. धोकादायक कृती थांबवा आणि Live Intelligence मधील सुरक्षा सूचना पाळा.':n?`मी परिस्थितीचे विश्लेषण केले आहे. पुढील कृती: ${n}.`:'मी परिस्थितीचे विश्लेषण केले आहे. Live Intelligence मधील पुढील कृती पहा.';if(language==='Hindi')return m?`आपके आवेदन के लिए ${m} आवश्यक है और यह उपलब्ध नहीं है।${n?` अगला कदम: ${n}।`:''}${d?` ${d} से पहले पूरा करें।`:''}`:high?'यह स्थिति जोखिम भरी हो सकती है। जोखिम वाली कार्रवाई रोकें और Live Intelligence में दिए सुरक्षा निर्देशों का पालन करें।':n?`मैंने स्थिति का विश्लेषण किया है। अगला कदम: ${n}।`:'मैंने स्थिति का विश्लेषण किया है। Live Intelligence में अगला कदम देखें।';if(language==='Hinglish / Roman')return m?`Aapke application ke liye ${m} required hai aur available nahi hai.${n?` Next step: ${n}.`:''}${d?` ${d} se pehle complete karein.`:''}`:high?'Ye situation risky ho sakti hai. Risky action roko aur Live Intelligence ki safety guidance follow karo.':n?`Maine situation analyze ki hai. Next step: ${n}.`:'Maine situation analyze ki hai. Live Intelligence mein next action dekho.';return m?`Your application requires ${m}, and it is not available.${n?` Next step: ${n}.`:''}${d?` Complete it before ${d}.`:''}`:high?'This situation may be risky. Pause the risky action and follow the protective guidance in Live Intelligence.':n?`I analyzed the situation. Your next step is ${n}.`:'I analyzed the situation. See Live Intelligence for the next recommended action.';}


export default App;
