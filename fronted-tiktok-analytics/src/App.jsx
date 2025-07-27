import React, { useState, useEffect, useCallback, useRef } from 'react';

// --- Helper: Icon Components using SVG for simplicity ---
const DollarSignIcon = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
);
const GemIcon = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 3h12l4 6-10 13L2 9Z"></path><path d="M12 22V9"></path><path d="m3.5 8.5 17 0"></path><path d="m2 9 4-6"></path><path d="m22 9-4-6"></path></svg>
);
const CoinsIcon = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="8" cy="8" r="6"></circle><path d="M18.09 10.37A6 6 0 1 1 10.34 18"></path><path d="M7 6h1v4"></path><path d="M15 6h1v4"></path><path d="M12 12h1v4"></path></svg>
);
const GiftIcon = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 12 20 22 4 22 4 12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path></svg>
);
const TrophyIcon = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"></path><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"></path><path d="M18 2H6v7c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V2Z"></path></svg>
);
const ZapIcon = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
);
const AwardIcon = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="8" r="6"></circle><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"></path></svg>
);


// --- NEW: Animated Number Component ---
const AnimatedNumber = ({ value, isCurrency = false }) => {
    const [currentValue, setCurrentValue] = useState(0);
    const prevValueRef = useRef(0);

    useEffect(() => {
        const startValue = prevValueRef.current;
        const endValue = value;
        prevValueRef.current = value;
        
        let startTime = null;
        const duration = 700; // Animation duration in ms

        const animate = (timestamp) => {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            const animatedValue = startValue + (endValue - startValue) * progress;
            
            setCurrentValue(animatedValue);

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);

    }, [value]);

    if (isCurrency) {
        return `$${currentValue.toFixed(2)}`;
    }
    return currentValue.toLocaleString(undefined, { maximumFractionDigits: 0 });
};


// --- Individual Components (Refactored for Bootstrap & Animation) ---

const SummaryCard = ({ title, value, icon, colorClass, isCurrency }) => (
    <div className="col">
        <div className="card bg-body-secondary h-100 border-secondary">
            <div className="card-body d-flex align-items-center">
                <div className={`p-3 rounded-circle me-3 ${colorClass}`}>
                    {icon}
                </div>
                <div>
                    <div className="text-muted">{title}</div>
                    <div className="fs-4 fw-bold">
                        <AnimatedNumber value={value} isCurrency={isCurrency} />
                    </div>
                </div>
            </div>
        </div>
    </div>
);

const Leaderboard = ({ data, isLoading }) => {
    // FIXED: Calculate dynamic height for the container to prevent overlapping
    const containerHeight = data.length * 65; // 65px height per item

    return (
        <div className="card bg-body-secondary h-100 border-secondary">
            <div className="card-body">
                <h5 className="card-title fw-bold mb-3 d-flex align-items-center">
                    <TrophyIcon className="me-2 text-warning" /> Top Contributors (USD)
                </h5>
                <div 
                    className="list-group list-group-flush position-relative" 
                    // FIXED: Apply dynamic height and a smooth transition
                    style={{ 
                        height: `${containerHeight}px`,
                        transition: 'height 0.5s ease-in-out'
                    }}
                >
                    {isLoading && !data.length ? (
                        <div className="text-center text-muted py-5">Loading...</div>
                    ) : !isLoading && !data.length ? (
                         <div className="text-center text-muted py-5">No data found for this stream.</div>
                    ) : (
                        data.map((player, index) => (
                            <div 
                                key={player.playerId} 
                                className="list-group-item bg-transparent d-flex justify-content-between align-items-center px-0 animate-leaderboard-item"
                                style={{ 
                                    '--rank': index, 
                                    transition: 'top 0.5s ease-in-out', 
                                    top: `${index * 65}px`, 
                                    position: 'absolute', 
                                    width: 'calc(100% - 1.5rem)' 
                                }}
                            >
                                <div className="d-flex align-items-center">
                                    <span className="fw-bold text-muted me-3" style={{width: '20px'}}>{player.rank}</span>
                                    <div>
                                        <div className="fw-semibold">{player.playerName}</div>
                                        <div className="small text-muted">{player.playerId}</div>
                                    </div>
                                </div>
                                <div className="text-end">
                                    <div className="fw-bold text-success fs-5">
                                        <AnimatedNumber value={player.totalUSD} isCurrency={true} />
                                    </div>
                                    <div className="small text-muted">
                                        <AnimatedNumber value={player.totalValue} /> game currency
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

const LiveFeed = ({ data, isLoading }) => (
    <div className="card bg-body-secondary h-100 border-secondary d-flex flex-column">
        <div className="card-body">
            <h5 className="card-title fw-bold mb-3 d-flex align-items-center">
                <ZapIcon className="me-2 text-info" /> Live Gift Feed
            </h5>
            <div className="list-group list-group-flush custom-scrollbar" style={{ height: '450px', overflowY: 'auto' }}>
                 {isLoading && !data.length ? (
                    <div className="text-center text-muted py-5">Loading...</div>
                 ) : !isLoading && !data.length ? (
                    <div className="text-center text-muted py-5">Listening for new gifts...</div>
                 ) : data.map((gift) => (
                    <div key={`${gift.playerId}-${gift.timestamp}`} className="list-group-item list-group-item-action bg-transparent border-0 d-flex align-items-center animate-fade-in px-0">
                        <div className="p-2 bg-dark rounded-circle me-3">
                            <GiftIcon className="text-danger" />
                        </div>
                        <div className="flex-grow-1">
                            <p className="mb-0">
                                <span className="fw-semibold">{gift.playerName}</span> <span className="text-muted">sent a</span> {gift.originalGiftName}
                            </p>
                            <p className="small mb-0">
                               Value: <span className="fw-bold text-success">${gift.usd_value.toFixed(2)}</span>
                            </p>
                        </div>
                         <small className="text-muted">{new Date(gift.timestamp).toLocaleTimeString()}</small>
                    </div>
                ))}
            </div>
        </div>
    </div>
);

// --- Main App Component ---

export default function App() {
    const API_BASE_URL = "https://tiktok-api-740043250466.us-central1.run.app"; 
    
    const [roomId, setRoomId] = useState('live_stream_1');
    const [summaryData, setSummaryData] = useState({ grand_total_usd: 0, currency_totals: {} });
    const [leaderboardData, setLeaderboardData] = useState([]);
    const [feedData, setFeedData] = useState([]);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (API_BASE_URL === "https://tiktok-api-740043250466.us-central1.run.app") {
            setError("Please update the API_BASE_URL constant in the code with your deployed API service URL.");
            setIsLoading(false);
        }
    }, [API_BASE_URL]);

    const fetchData = useCallback(async () => {
        if (!roomId) return;
        setIsLoading(true);
        
        try {
            const [summaryRes, leaderboardRes, feedRes] = await Promise.all([
                fetch(`${API_BASE_URL}/streams/${roomId}/summary?minutes=60`),
                fetch(`${API_BASE_URL}/streams/${roomId}/leaderboard?minutes=60`),
                fetch(`${API_BASE_URL}/streams/${roomId}/feed?limit=15`)
            ]);

            if (!summaryRes.ok || !leaderboardRes.ok || !feedRes.ok) {
                throw new Error(`API request failed. Status: ${summaryRes.status}, ${leaderboardRes.status}, ${feedRes.status}`);
            }

            const summary = await summaryRes.json();
            const leaderboard = await leaderboardRes.json();
            const feed = await feedRes.json();

            setError(null);
            setSummaryData(summary);
            setLeaderboardData(leaderboard.leaderboard || []);
            setFeedData(prevFeed => {
                const newItems = feed.filter(newItem => !prevFeed.some(oldItem => oldItem.timestamp === newItem.timestamp));
                return [...newItems, ...prevFeed].slice(0, 50);
            });

        } catch (err) {
            console.error("Failed to fetch data:", err);
             if (err instanceof TypeError && err.message.includes('Failed to fetch')) {
                 setError("A network error occurred. This is most likely a CORS issue. Please ensure your backend API has CORS enabled.");
            } else {
                 setError(`Failed to connect to the API: ${err.message}`);
            }
        } finally {
            setIsLoading(false);
        }
    }, [roomId, API_BASE_URL]);

    useEffect(() => {
        fetchData(); 
        const intervalId = setInterval(fetchData, 4000); 
        return () => clearInterval(intervalId);
    }, [fetchData]);

    const handleRoomIdSubmit = (e) => {
        e.preventDefault();
        const newRoomId = e.target.elements.roomIdInput.value;
        if (newRoomId) {
            setRoomId(newRoomId);
            setFeedData([]);
            setLeaderboardData([]);
            setSummaryData({ grand_total_usd: 0, currency_totals: {} });
        }
    }
    
    const currencyIcons = {
        'GEMS': <GemIcon className="text-primary" />,
        'COINS': <CoinsIcon className="text-warning" />,
        'POWER_UP': <ZapIcon className="text-info" />,
        'ACHIEVEMENT': <AwardIcon className="text-danger" />,
    };

    return (
        <div className="container-fluid py-4 px-md-5">
            <header className="mb-5">
                <h1 className="display-4 fw-bold">Live Stream Analytics Dashboard</h1>
                <p className="text-muted fs-5">Real-time gift and contribution monitoring</p>
                <form onSubmit={handleRoomIdSubmit} className="mt-4" style={{maxWidth: '500px'}}>
                    <div className="input-group">
                        <input 
                            type="text"
                            name="roomIdInput"
                            defaultValue={roomId}
                            className="form-control form-control-lg"
                            placeholder="Enter Live Stream Room ID"
                        />
                        <button type="submit" className="btn btn-primary btn-lg">
                            Monitor
                        </button>
                    </div>
                </form>
            </header>

            {error && <div className="alert alert-danger">{error}</div>}

            <div className="row row-cols-1 row-cols-md-2 row-cols-xl-4 g-4 mb-5">
                <SummaryCard 
                    title="Total Revenue (USD)"
                    value={summaryData?.grand_total_usd || 0}
                    icon={<DollarSignIcon className="text-success" />}
                    colorClass="bg-success-subtle"
                    isCurrency={true}
                />
                {Object.entries(summaryData?.currency_totals || {}).map(([type, value]) => (
                    <SummaryCard
                        key={type}
                        title={`Total ${type}`}
                        value={value}
                        icon={currencyIcons[type] || <GiftIcon className="text-secondary" />}
                        colorClass="bg-secondary-subtle"
                     />
                ))}
            </div>

            <div className="row g-5">
                <div className="col-lg-6">
                    <Leaderboard data={leaderboardData} isLoading={isLoading} />
                </div>
                <div className="col-lg-6">
                    <LiveFeed data={feedData} isLoading={isLoading} />
                </div>
            </div>
             <footer className="text-center text-muted mt-5 py-4">
                <p>Dashboard polling API every 4 seconds. UI by Jaimeardp.</p>
            </footer>
        </div>
    );
}
