import React, {useEffect, useState} from 'react'
import axios from 'axios'
import './flexbox.css'
import Clock from './Clock'
import CircularProgress from '@mui/material/CircularProgress';

function Prediction() {
    const [inputText, setInputText] = useState('');
    const [response, setResponse] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const handleSubmit = async () => {
        setIsLoading(true);
        setResponse(null);
        try {
            // Could put loading circle here
            const res = await axios.post('http://127.0.0.1:5000/predict', {text: inputText});
            setResponse(res.data);
        } catch (error) {
            console.error("Prediction error:", error);
            setResponse({error: "Failed to fetch prediction." });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{padding: 20}} className={"diagnostic-title"}>
            <Clock />
            <h2> Diagnostic Chatbot</h2>
            <fieldset>
                <legend>Please describe your symptoms</legend>
                <textarea rows="4"
                          cols="50"
                          value={inputText}
                          onChange={e =>setInputText(e.target.value)}
                />
                <br />
                <button onClick={handleSubmit} className={"submit-button"}>Submit</button>
                {isLoading && (
                    <div className="loading-spinner">
                        {/*<CircularProgress />*/}
                        <span style={{marginLeft: '10px', fontSize: '16px'}}>Analyzing symptoms</span>
                    </div>
                )}
                {!isLoading && response && (
                    <pre>{JSON.stringify(response, null, 2)}</pre>
                )}
            </fieldset>


        </div>
    );
}

export default Prediction;
