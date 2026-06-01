import { useState, useRef } from 'react';
import axios from 'axios';

const API = `http://${window.location.hostname}:5000`;

const MODES = [
  { id: 'camera', icon: '📸', label: 'Live Camera' },
  { id: 'image', icon: '🖼️', label: 'Upload Image' },
  { id: 'video', icon: '🎬', label: 'Upload Video' }
];

export default function App() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [image, setImage] = useState(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [error, setError] = useState('');
  const [activeMode, setActiveMode] = useState('image');
  const [stats, setStats] = useState(null);
  
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const canvasRef = useRef(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: {ideal:1280}, height: {ideal:720} }
      });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraOn(true);
      setError('');
    } catch(e) {
      setError('Camera permission denied. Please allow camera access.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    setCameraOn(false);
  };

  const handleModeSwitch = (modeId) => {
    setActiveMode(modeId);
    setText('');
    setImage(null);
    setError('');
    if (modeId === 'camera') {
      startCamera();
    } else {
      stopCamera();
    }
  };

  const capturePhoto = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const base64 = canvas.toDataURL('image/jpeg', 0.95);
    setImage(base64);
    stopCamera();
    await processBase64(base64, 'camera');
  };

  const processBase64 = async (base64, inputType) => {
    setLoading(true);
    setText('');
    setError('');
    try {
      const res = await axios.post(`${API}/predict`, {
        image_base64: base64,
        input_type: inputType
      });
      if (res.data.success) {
        setText(res.data.text);
        setStats({ chars: res.data.characters_detected, type: 'Image/Camera' });
      } else {
        setError(res.data.error || 'Detection failed');
      }
    } catch(e) {
      setError('Cannot connect to AI Backend. Ensure app.py is running.');
    }
    setLoading(false);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (activeMode === 'video' && file.type.startsWith('video/')) {
      setLoading(true);
      setText('');
      setError('');
      const form = new FormData();
      form.append('video', file);
      try {
        const res = await axios.post(`${API}/predict_video`, form);
        if (res.data.success) {
          setText(res.data.text);
          setStats({ chars: res.data.frames_processed, type: 'Video Frames' });
        }
      } catch(e) {
        setError('Video processing failed');
      }
      setLoading(false);
      return;
    }

    const reader = new FileReader();
    reader.onload = async (ev) => {
      setImage(ev.target.result);
      await processBase64(ev.target.result, 'image');
    };
    reader.readAsDataURL(file);
  };

  const speakText = async (t) => {
    if (!t || t === '?') return;
    setSpeaking(true);
    try {
      await axios.post(`${API}/speak`, { text: t });
    } catch {
      const u = new SpeechSynthesisUtterance(`The Braille reads: ${t}`);
      u.lang = 'en-IN';
      u.rate = 0.9;
      window.speechSynthesis.speak(u);
    }
    setTimeout(() => setSpeaking(false), 2000);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f0c29, #302b63, #24243e)',
      fontFamily: "'Segoe UI', system-ui, sans-serif",
      color: 'white',
      paddingBottom: '40px'
    }}>
      {/* Header */}
      <div style={{
        background: 'rgba(255,255,255,0.03)',
        backdropFilter: 'blur(16px)',
        padding: '20px 24px',
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        borderBottom: '1px solid rgba(255,255,255,0.05)',
        boxShadow: '0 4px 30px rgba(0, 0, 0, 0.1)'
      }}>
        <span style={{fontSize: 32}}>👁️</span>
        <div>
          <h1 style={{margin:0, fontSize:24, fontWeight:800, color:'#60a5fa', letterSpacing: '-0.5px'}}>
            BrailleVision AI
          </h1>
          <p style={{margin:0, fontSize:12, color:'rgba(255,255,255,0.5)', marginTop: '2px'}}>
            Supports: Handwritten, Embossed, & Full Pages
          </p>
        </div>
        <div style={{
          marginLeft:'auto', background:'rgba(16, 185, 129, 0.2)', color: '#34d399',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius:20, padding:'6px 14px', fontSize:11, fontWeight:700, letterSpacing: '1px'
        }}>● SYSTEM ONLINE</div>
      </div>

      <div style={{maxWidth:600, margin:'0 auto', padding:'32px 20px'}}>
        
        {/* Sleek Mode Selector */}
        <div style={{
          display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap: 12, marginBottom: 30,
          background: 'rgba(0,0,0,0.2)', padding: '8px', borderRadius: '16px'
        }}>
          {MODES.map(mode => (
            <button key={mode.id} onClick={() => handleModeSwitch(mode.id)} style={{
              background: activeMode === mode.id ? 'linear-gradient(135deg, #3b82f6, #1d4ed8)' : 'transparent',
              border: 'none', borderRadius: '12px', padding: '12px 8px',
              color: activeMode === mode.id ? 'white' : 'rgba(255,255,255,0.5)',
              cursor: 'pointer', fontSize: 13, fontWeight: 600, transition: 'all 0.3s',
              boxShadow: activeMode === mode.id ? '0 4px 15px rgba(59, 130, 246, 0.4)' : 'none'
            }}>
              <span style={{fontSize: 18, marginRight: 6}}>{mode.icon}</span> 
              {mode.label}
            </button>
          ))}
        </div>

        {/* Camera UI */}
        {activeMode === 'camera' && cameraOn && (
          <div style={{marginBottom:24, animation: 'fadeIn 0.5s'}}>
            <div style={{
              borderRadius: '20px', overflow:'hidden', border:'2px solid rgba(59,130,246,0.5)', 
              position:'relative', boxShadow: '0 10px 30px rgba(0,0,0,0.3)'
            }}>
              <video ref={videoRef} autoPlay playsInline style={{width:'100%', display:'block'}}/>
              <div style={{
                position:'absolute', top:'50%', left:'50%', transform:'translate(-50%,-50%)',
                border:'2px dashed rgba(255,255,255,0.6)', width:'80%', height:'40%', borderRadius:12
              }}/>
            </div>
            <canvas ref={canvasRef} style={{display:'none'}}/>
            <button onClick={capturePhoto} style={{
              width: '100%', marginTop: 16, background:'linear-gradient(135deg,#10b981,#059669)',
              border:'none', borderRadius:16, padding:'18px', color:'white', fontSize:16, 
              cursor:'pointer', fontWeight:700, boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)'
            }}>
              📸 Scan & Translate
            </button>
          </div>
        )}

        {/* Upload UI */}
        {activeMode !== 'camera' && (
          <label style={{
            display:'block', background:'rgba(255,255,255,0.03)',
            border:'2px dashed rgba(255,255,255,0.1)', borderRadius: '24px', padding:'48px 20px',
            textAlign:'center', cursor:'pointer', marginBottom:24, transition:'all 0.3s'
          }}>
            <div style={{fontSize:48, marginBottom:16}}>{MODES.find(m=>m.id===activeMode).icon}</div>
            <p style={{margin:'0 0 8px', fontWeight:600, fontSize: 18, color:'#93c5fd'}}>
              {activeMode === 'video' ? 'Drop a Video Here' : 'Drop an Image Here'}
            </p>
            <p style={{margin:0, fontSize:13, color:'rgba(255,255,255,0.4)'}}>Or click to browse your files</p>
            <input type="file" accept={activeMode === 'video' ? 'video/*' : 'image/*'} 
                   onChange={handleFileUpload} style={{display:'none'}}/>
          </label>
        )}

        {/* Image Preview */}
        {image && activeMode === 'image' && !loading && !text && (
          <img src={image} alt="preview" style={{width:'100%', borderRadius: '20px', marginBottom: 24, border: '1px solid rgba(255,255,255,0.1)'}}/>
        )}

        {/* Loading State */}
        {loading && (
          <div style={{
            background:'rgba(59,130,246,0.1)', border:'1px solid rgba(59,130,246,0.2)',
            borderRadius: '20px', padding: '32px 20px', textAlign:'center', marginBottom:24
          }}>
            <div style={{fontSize:32, marginBottom:12, animation: 'spin 2s linear infinite'}}>⚙️</div>
            <p style={{margin:0, color:'#93c5fd', fontSize: 16, fontWeight:600}}>AI is processing...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div style={{ background:'rgba(239,68,68,0.1)', border:'1px solid rgba(239,68,68,0.3)', borderRadius:16, padding:16, marginBottom:24, color:'#fca5a5', textAlign: 'center' }}>
            ⚠️ {error}
          </div>
        )}

        {/* Final Result Box */}
        {text && !loading && (
          <div style={{
            background:'rgba(16, 185, 129, 0.05)', border:'1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: '24px', padding: '32px', textAlign: 'center',
            boxShadow: '0 10px 40px rgba(16, 185, 129, 0.1)'
          }}>
            <p style={{margin:'0 0 16px', fontSize:12, color:'#6ee7b7', textTransform:'uppercase', letterSpacing: 2, fontWeight: 700}}>
              Translation Complete
            </p>
            <p style={{
              margin:'0 0 32px', fontSize: text.length > 20 ? 32 : 56, 
              fontWeight:800, color:'#ffffff', textTransform:'uppercase',
              lineHeight: 1.2
            }}>{text}</p>
            
            <button onClick={() => speakText(text)} disabled={speaking} style={{
                width:'100%', background: speaking ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #f59e0b, #d97706)',
                border:'none', borderRadius: '16px', padding:'16px', color:'white', fontSize:16, fontWeight:700,
                cursor: speaking ? 'not-allowed' : 'pointer', boxShadow: speaking ? 'none' : '0 4px 15px rgba(245, 158, 11, 0.3)'
              }}>
              {speaking ? '🔊 Synthesizing Audio...' : '🔊 Read Aloud'}
            </button>
          </div>
        )}

      </div>
    </div>
  );
}