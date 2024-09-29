import React from 'react';
import AppNavbar from '../Navigation/AppNavbar'; // Your Navbar component
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import Modal from './Modal';
import leaves from '../art_assets/leaves.png';
import icon from '../art_assets/seed_logo.png';
import SDGSelector from './SDGSelector';
import NewsFeed from './Newsfeed';
import Chart from 'chart.js/auto';
import { Line } from 'react-chartjs-2';
import { Pie } from 'react-chartjs-2';
import Popup from '../Popup/Popup.js';
import sdgData from './sdgData.js';

const fetchStockInfo = async (stockSymbol) => {
    try {
      const url = `http://127.0.0.1:5002/stock?ticker=${stockSymbol.toUpperCase()}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Network response was not ok');
      
      const data = await response.json();
      
      return {
        name: data.companyName,
        symbol: data.symbol,
        currentPrice: data.currentPrice,
        marketCap: data.marketCap,
        '52WeekHigh': data['52WeekHigh'],
        '52WeekLow': data['52WeekLow'],
        esg: data.esg,
        es: data.es,
        gs: data.gs,
        ss: data.ss,
        beta: data.beta,
        dividendYield: data.dividendYield,
        peRatio: data.peRatio,
        chartData: [data.day0, data.day1, data.day2, data.day3, data.day4, data.day5],
        sector: data.sector,
      };
    } catch (error) {
      console.error("Failed to fetch stock info:", error);
      return null;
    }
  };

const pageVariants = {
    initial: { opacity: 0 },
    in: { opacity: 1 },
    out: { opacity: 0 }
};

const pageTransition = {
    type: "tween",
    ease: "anticipate",
    duration: 0.5
};

function Dashboard() {
    const parsePortfolio = (response) => {
        try {
            var parsedResponse = JSON.parse(response)
            let a = {
                portfolio: parsedResponse.portfolio,
                justification: parsedResponse.justification
            }
    
            let tickers = []
            let percentages = []
    
            a.portfolio.forEach((obj) => {
                tickers.push(obj.ticker)
                percentages.push(obj.percentage)
            })

            setData(tickers)
            setPercentages(percentages)
            prevObjects.push(a.portfolio)
            setPrevObjects(prevObjects)
            setJustification(a.justification)
            
            return {
                portfolio: parsedResponse.portfolio,
                justification: parsedResponse.justification
            }
    
        } catch (error) {
            console.error("Failed to parse portfolio:", error);
            return null;
        }
    };

    const [data, setData] = useState([])
    const [percentages, setPercentages] = useState([])
    const [justification, setJustification] = useState('')

    const [searchTerm, setSearchTerm] = useState('');

    //For initial Modal
    const [modalOpen, setModalOpen] = useState(true);
    const [canCloseModal, setCanCloseModal] = useState(false);
    
    const [experience, setExperience] = useState(0);
    const [amount, setAmount] = useState(null);
    const [pastAmounts, setPastAmounts] = useState([0, 0]);
    const [philosophy, setPhilosophy] = useState(null);
    
    const [selectedSDGs, setSelectedSDGs] = useState([]);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const handleSDGSelectionChange = (selectedIds) => {
        setSelectedSDGs(selectedIds);
    };

    const [mapping, setMapping] = useState({});
    const [ctx, setCtx] = useState('');
    const [fetchingData, setFetchingData] = useState(false)
    const [creatingNewPortfolio, setCreatingNewPortfolio] = useState(false)

    const [prevObjects, setPrevObjects] = useState([])

    const createNewPortfolio = async () => {
        setIsRefreshing(true)
        setCreatingNewPortfolio(true)

        try {
            const url = `http://127.0.0.1:5002/func`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();
            parsePortfolio(data)
            console.log("Fetched stock data:", data);
        } catch(error) {
            console.log("Error in API call: " + error)
        }

        setIsRefreshing(false)
        setCreatingNewPortfolio(false)
    }

    const followUpAPI = async (ctx) => {
        console.log(ctx)

        setFetchingData(true)
        setIsRefreshing(true)

        try {
            const url = `http://127.0.0.1:5002/func?cntxt=` + ctx + `?new=false`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();
            parsePortfolio(data)
            console.log("Fetched stock data:", data);
        } catch(error) {
            console.log("Error in API call: " + error)
        }

        setIsRefreshing(false);
        setFetchingData(false)
    }

    const fetchData = async () => {
        setIsRefreshing(true);
        // Simulate fetch call
        try {
            var sdgString = "";

            selectedSDGs.map(idx => {
                sdgString += sdgData[idx-1].name + ", "
            })

            const url = `http://127.0.0.1:5002/func?cntxt=` + sdgString + ". My investment philosophy is: (ignore if blank)" + philosophy;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();
            parsePortfolio(data)
            console.log("Fetched stock data:", data);
        } catch(error) {
            console.log("Error in API call: " + error)
        }

        setIsRefreshing(false);
        setFetchingData(false);
      };
    
      useEffect(() => {
        if (!modalOpen && isRefreshing && data.length == 0) {
          fetchData();
        } else if (!modalOpen && isRefreshing && !fetchingData) {
            followUpAPI()
        } else if (!modalOpen && isRefreshing && !creatingNewPortfolio) {
            createNewPortfolio()
        } 
      }, [isRefreshing]);


    const handleCloseModal = () => {
        if (canCloseModal) {
            setModalOpen(false);
            setPastAmounts(prev => [...prev, amount]);
            //Fetch needed clusters
            setIsRefreshing(true);
        }
    };  

    const chartOptions = {
        plugins: {
            legend: {
                display: false, // Hide legend
            },
        },
        elements: {
            point: {
                radius: 0, // Hide points on the line
            },
        },
        scales: {
            x: {
                ticks: {
                    color: 'white', // Set x-axis tick color to white
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)', // Set x-axis grid line color to white with low opacity
                }
            },
            y: {
                ticks: {
                    color: 'white', // Set y-axis tick color to white
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)', // Set y-axis grid line color to white with low opacity
                }
            }
        },
        maintainAspectRatio: true,
        responsive: true,
    };
    

    useEffect(() => {
        // Update canCloseModal based on amount and experience conditions
        // const isEligibleToClose = amount >= 10 && experience > 0;
        setCanCloseModal(true);
    }, []); 

    const [hoverData, setHoverData] = useState('');
    const [textInput, setTextInput] = useState('');

    const pieData = {
        labels: data, //All ticker names
        datasets: [
            {
                label: 'Current Portfolio',
                data: percentages,
                backgroundColor: generateColorShadesForPie("hsl(119, 49%, 56%)", data.length),
                hoverOffset: 4,
            },
        ],
    };

    const pieOptions = {
        plugins: {
            legend: {
                labels: {
                    color: 'white',
                },
            },
        },
        interaction: {
            intersect: true,
            mode: 'point',
        },
        responsive: true,
        maintainAspectRatio: true,
        onHover: async (event, chartElement) => {
            if (chartElement.length) {
                const index = chartElement[0].index;
                const label = pieData.labels[index];
                const stockSymbol = label; // Assuming label is the stock symbol
                const stockInfo = mapping[stockSymbol]; // Fetch stock information
                setHoverData(prev => {
                    if (stockInfo && stockInfo !== prev) {
                        return (
                            <div className="mx-auto shadow-lg rounded-md bg-white w-full h-full flex flex-row p-2">
    <div className='flex flex-row w-full justify-between'>
        {/* Left Column for Name, Symbol, Current Price, and Sector */}
        <div className='flex flex-col justify-start w-1/2'>
            <div className="text-center font-bold text-md">
                {stockInfo.name} ({stockInfo.symbol})
            </div>
            <div className="text-center">
                <div className="text-sm font-semibold mt-2">
                    Current Price: <span className="text-green-600">${stockInfo.currentPrice}</span>
                </div>
                <p className='text-sm'>{stockInfo.name} is a U.S. Publicly Traded Company in the {stockInfo.sector} Sector.</p>
            </div>
        </div>

        {/* Right Column for ESG and other scores */}
        <div className="flex flex-col justify-center items-center w-1/2">
            <div className="font-semibold w-fit">ESG Score: <span className="text-green-600">{stockInfo.esg}</span></div>
            <div className="font-semibold">Environmental Score: <span className="text-green-600">{stockInfo.es}</span></div>
            <div className="font-semibold">Social Score: <span className="text-green-600">{stockInfo.ss}</span></div>
            <div className="font-semibold">Governmental Score: <span className="text-green-600">{stockInfo.gs}</span></div>
        </div>
    </div>
</div>
                     
                        );
                    } else {
                        return null;
                    }
                });
            } else {
                setHoverData(null);
            }
        }}

    function generateColorShadesForPie(initialColorHSL, n) {
        // Parse the initial color HSL values
        let [hue, saturation, lightness] = initialColorHSL.match(/\d+/g).map(Number);
      
        const colors = [initialColorHSL]; // Include the initial color in the array
      
        for (let i = 1; i < n; i++) {
          // Adjust lightness and saturation for each new color
          lightness = (lightness + 10) % 100;
          saturation = (saturation + 5) % 100;
      
          // Ensure lightness stays within a visually appealing range
          if (lightness > 90) lightness -= 30;
          if (saturation < 30) saturation += 20;
      
          colors.push(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
        }
      
        return colors;
      }

    return (
        <motion.div
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
        >
            {isRefreshing && (
        <div className="overlay">
          <div className="spinner"></div>
        </div>
      )}
            <Modal show={modalOpen}>
            <div className="flex flex-col items-left w-full relative overflow-hidden p-5 h-full">
                    <div className="flex items-left mb-3">
                        <h2 className="text-left text-2xl font-bold mr-4">Proceed to surgery</h2>
                        <img src={icon} alt="Icon" className="w-10 h-10 rounded-xl"/>
                    </div>
                    <div className="flex flex-row w-full relative h-full">
                    <div className="w-1/2 h-full bg-[#ffffff] rounded-xl">
                        <iframe src="./patient.html" title="HTML Document" className="w-full h-full"></iframe>
                    </div>
                    <div className="w-1/2 h-full flex flex-col  p-0 rounded-xl">
                    <div className="w-full h-5/6 flex flex-col rounded-xl">
                        <div className="w-full flex-grow">
                            <iframe 
                                src="http://127.0.0.1:7860/" 
                                className="w-full h-full rounded-xl" 
                                frameBorder="0" 
                                allow="autoplay; encrypted-media" 
                                allowFullScreen 
                                title="Gradio app"
                            ></iframe>
                        </div>
                    </div>
                    <div className="flex items-center w-full mb-5 p-5">
                        <p className="w-4/12 text-left font-medium flex items-center">Additional Notes?</p>
                        <div className="flex items-center w-full ml-1">
                            <div className="relative rounded-md shadow-sm w-full flex items-center">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-activity" viewBox="0 0 16 16">
                                    <path fill-rule="evenodd" d="M6 2a.5.5 0 0 1 .47.33L10 12.036l1.53-4.208A.5.5 0 0 1 12 7.5h3.5a.5.5 0 0 1 0 1h-3.15l-1.88 5.17a.5.5 0 0 1-.94 0L6 3.964 4.47 8.171A.5.5 0 0 1 4 8.5H.5a.5.5 0 0 1 0-1h3.15l1.88-5.17A.5.5 0 0 1 6 2"/>
                                </svg>
                                </div>
                                <input type="text" name="philosophy" placeholder="Additional clinical notes for EHR updates?"
                                    onChange={(e) => setPhilosophy(e.target.value)} value={philosophy}
                                    className="focus:ring-black/[0.5] block w-full pl-10 pr-4 py-2 bg-white text-black text-sm rounded-md focus:outline-none focus:ring-1 dark:bg-white dark:placeholder-gray-400 dark:text-black dark:focus:ring-black/[0.5] dark:focus:border-black" />
                            </div>
                        </div>
                    </div>
                    <div className="flex justify-end">
                        <button 
                            type='submit'
                            onClick={() => handleCloseModal()} 
                            disabled={!canCloseModal} 
                            className={`text-white text-sm py-3 px-8 rounded-full ${canCloseModal ? 'bg-[#050505] hover:bg-[#1C281E]/[0.5]' : 'bg-gray-500 text-gray-200'}`}
                        >
                            {canCloseModal ? 'Proceed' : 'Fill this out...'}
                        </button>
                    </div>   
                </div>
                </div>
                </div>
            </Modal>


        <div className="h-screen flex flex-col">
            {/* Navbar */}
            <div className="w-full">
                <AppNavbar />
            </div>
            <div className='flex flex-row items-center justify-center h-full overflow-x-hidden p-4'>
                <div className='flex flex-col h-full w-1/2 p-2 justify-start rounded-xl'>
                        {/* Pie Chart */}
                        <div className='bg-[#142629] h-full w-full flex flex-col rounded-xl p-5 justify-start'>
                        <h2 className='text-lg font-md text-white mb-16'>Live Surgery Stream</h2>
                            <div className='w-full h-1/3 flex items-center justify-center'>
                                <video width="800px" height="300px" controls>
                                    <source src="./mohs.mp4" type="video/mp4"/>
                                    Your browser does not support the video tag.
                                </video>
                            </div>

                            <h2 className='text-lg font-md text-white mt-16 mb-16'>Surgical Annotation</h2>
                            {/* Embed a video with Tailwind CSS styling */}
                            <div className='w-full h-1/3 flex items-center justify-center'>
                            <video
                                src="/vid.mov"  // Replace with the actual path to your video file
                                width="700px" height="200px"
                                autoplay
                                loop
                                controls
                                title="Surgical Annotation"
                            >
                                Your browser does not support the video tag.
                            </video>
                            </div>
                            {/* Text Input - Ensure it's at the bottom */}
                            <div className='w-full flex flex-row items-end h-full'>
                            <form className="w-full flex h-full items-end">
                                <input
                                    type="text"
                                    value={textInput}
                                    onChange={(e) => setTextInput(e.target.value)}
                                    className="bg-white text-black text-sm rounded-md focus:ring-2 block w-3/4 p-3 focus:outline-none focus:ring-black/[0.5]"
                                    placeholder="Flag actions taken by the surgeon!"
                                />
                                <button 
                                    type='submit'
                                    onClick={(e) => {
                                        e.preventDefault(); 
                                        followUpAPI(textInput); 
                                        setTextInput("");
                                    }} 
                            className='text-sm bg-[#000000] hover:opacity-[0.8] text-white font-md py-2 px-4 rounded-full w-1/4 ml-5 h-11' 
                        >
                            Flag
                        </button>                                
                        </form>
                    </div>
                    </div>
                </div>
                <div className="flex flex-col h-full w-1/2 text-white p-5">
  {/* Portfolio History Header */}
  <div className="mb-0 bg-black/[0.7] p-5 rounded-xl h-full">
    <h2 className="text-lg font-md text-white">Procedure History</h2>

    {/* Iframe Container */}
    <div className="w-full flex-grow mt-4 h-full mb-0">
      <iframe
        src="./three_js/transcript_34.html"  // Replace with the actual path to your HTML content
        className="w-full h-5/6 border-none rounded-lg shadow-lg mb-6"
        title="Portfolio Justification"
      ></iframe>
    </div>
  </div>
                </div>
            </div>
        </div>
        </motion.div>
    );
}

export default Dashboard;