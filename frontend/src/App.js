import { useState } from 'react';
import axios from 'axios';

export default function App() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [image, setImage] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImage(URL.createObjectURL(file));
    setLoading(true);
    const form = new FormData();
    form.append('image', file);
    try {
      const res = await axios.post('http://localhost:5000/predict', form);
      setText(res.data.text);
    } catch {
      setText('Error connecting to backend');
    }
    setLoading(false);
  };

  const speak = async () => {
    await axios.post('http://localhost:5000/speak', { text });
  };

  return (
    <div style={{padding:32, fontFamily:'sans-serif', maxWidth:600, margin:'auto'}}>
      <h1 style={{color:'#2563eb'}}>BrailleVision AI</h1>
      <p style={{color:'#666'}}>Real-time Braille to Text and Speech</p>
      
      <div style={{border:'2px dashed #ccc', padding:32, borderRadius:12, textAlign:'center', margin:'24px 0'}}>
        <input type="file" accept="image/*" onChange={handleUpload} id="upload" style={{display:'none'}}/>
        <label htmlFor="upload" style={{cursor:'pointer', color:'#2563eb', fontSize:18}}>
          📷 Click to upload Braille image
        </label>
      </div>

      {image && <img src={image} alt="uploaded" style={{width:'100%', borderRadius:8, marginBottom:16}}/>}
      
      {loading && <p style={{color:'#666'}}>🔍 Detecting Braille...</p>}
      
      {text && (
        <div style={{background:'#f0f9ff', padding:24, borderRadius:12}}>
          <h2>Decoded Text:</h2>
          <p style={{fontSize:28, letterSpacing:3, fontWeight:'bold', color:'#1e40af'}}>{text}</p>
          <button 
            onClick={speak}
            style={{background:'#2563eb', color:'white', border:'none', padding:'12px 24px', borderRadius:8, fontSize:16, cursor:'pointer'}}>
            🔊 Read Aloud
          </button>
        </div>
      )}
    </div>
  );
}