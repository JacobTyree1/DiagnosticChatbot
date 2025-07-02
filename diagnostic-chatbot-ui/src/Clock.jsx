import React, {useState, useEffect} from "react";

function Clock() {
    const [time, setTime] = useState(new Date());

    useEffect(() => {
        const timerId = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(timerId);
        }, []
    );

    return (
        <div>
            <h1>{time.toLocaleTimeString()}</h1>
        </div>
    );
}

export default Clock;