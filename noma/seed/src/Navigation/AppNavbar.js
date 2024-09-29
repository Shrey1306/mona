import { Fragment, useState, useRef, useEffect } from 'react';
import { Disclosure } from '@headlessui/react';
import { Line } from 'react-chartjs-2';
import Chart from 'chart.js/auto';
import seed from '../art_assets/seed_logo.png';
import avatar from '../art_assets/avatar.png';
import seed_text from '../art_assets/seed_text.png';

const navigation = [
  { name: 'Assisted Cases', href: '/dashboard', current: true }
];

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

const fetchStockInfo = async (stockSymbol) => {
  try {
    const url = `http://127.0.0.1:5002/stock?ticker=${stockSymbol.toUpperCase()}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Network response was not ok');
    
    const data = await response.json();
    console.log("Fetched stock data:", data); // Corrected to log for debugging purposes
    
    // Return all relevant data for future use, including financials and ESG scores
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
      // Additional data can be stored here as needed
    };
  } catch (error) {
    console.error("Failed to fetch stock info:", error);
    return null;
  }
};

export default function NavbarDefault() {
  const [searchTerm, setSearchTerm] = useState('');
  const [showHoverBox, setShowHoverBox] = useState(false);
  const [stockInfo, setStockInfo] = useState(null); // Initialize as null to properly handle conditional rendering
  const searchInputRef = useRef(null);
  
  useEffect(() => {
    const handleKeyDown = async (e) => {
      if (e.key === 'Enter') {
        e.preventDefault(); // Prevent the default form submit behavior
        const stockData = await fetchStockInfo(searchTerm);
        if (stockData) {
          setStockInfo(stockData);
          setShowHoverBox(true);
        } else {
          setShowHoverBox(false);
        }
      }
    };
    
    // const input = searchInputRef.current;
    // input.addEventListener('keydown', handleKeyDown);

    // return () => input.removeEventListener('keydown', handleKeyDown);
  }, []);

  const chartOptions = {
    plugins: {
      legend: {
        display: false, // Hides the legend
      },
      tooltip: {
        callbacks: {
          title: function(tooltipItems, data) {
            // Assuming your labels are set up as 'Day 1', 'Day 2', etc.
            // You can adjust this logic based on your actual labels setup
            return tooltipItems[0].label;
          },
          label: function(context) {
            let label = context.dataset.label || '';
  
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
            }
            return label;
          }
        }
      }
    },
    scales: {
      x: {
        ticks: {
          display: false,
        },
        beginAtZero: false
      },
      y: {
        ticks: {
          display: false,
        },
        beginAtZero: false
      }
    },
    maintainAspectRatio: false
  };  

  const chartData = {
    labels: stockInfo?.chartData?.map((_, index) => `Day ${index + 1}`) || [],
    datasets: [
      {
        label: `${stockInfo?.name} Stock Price`,
        data: stockInfo?.chartData || [],
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }
    ]
  };

  return (
    <Disclosure as="nav" className="bg-[#f5f1e3] rounded-b-xl shadow-lg">
      {({ open }) => (
        <>
          <div className="mx-auto w-full px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-3 w-full">
              <div className="flex items-center">
                <img className="h-16 w-auto rounded-2xl" src={seed} alt="Seed" />
                <img className="h-8 w-auto pl-5" src={seed_text} alt="Seed" />
              </div>
              <div className="flex items-center" ref={searchInputRef}>
                <div className="relative rounded-md shadow-sm w-full flex items-center">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
                                  <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"/>
                                </svg>
                                </div>
                    <input
                      type="text"
                      placeholder="Search through past cases..."
                      className="pl-10 bg-white text-black text-sm rounded-md focus:ring-2 block w-96 p-2 focus:outline-none focus:ring-black/[0.5]"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    {showHoverBox && stockInfo && (
                      <div className="absolute left-0 mt-2 max-w-4xl bg-white rounded-md shadow-lg p-4" 
                            style={{left: '50%', transform: 'translateX(-50%)', width: '50vw', top: '100%'}}>
                        <button onClick={() => setShowHoverBox(false)}
                                className="absolute top-0 right-0 mt-2 mr-2 text-lg font-semibold">
                          ×
                        </button>
                        {/* Company Name, Symbol, and Current Price, centered */}
                        <div className="text-center font-bold text-lg">
                          {stockInfo.name} ({stockInfo.symbol})
                        </div>
                        <div className="text-center">
                          <div className="text-center text-xl font-semibold mt-2">
                            Current Price: <span className="text-green-600">${stockInfo.currentPrice}</span>
                          </div>
                          <p>{stockInfo.name} is a U.S. Publicly Traded Company in the {stockInfo.sector} Sector.</p>
                        </div>
                      
                        {/* Container for split view */}
                        <div className="flex mt-4">
                          {/* Left Side: Financial Information Table */}
                          <div className="w-1/2 pr-2">
                            <table className="w-full">
                              <tbody>
                                <tr>
                                  <td className="px-2 py-1">Market Cap</td>
                                  <td className="px-2 py-1 text-right">
                                    {new Intl.NumberFormat('en-US').format(stockInfo.marketCap)}
                                  </td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1">52-Week High</td>
                                  <td className="px-2 py-1 text-right">${stockInfo['52WeekHigh']}</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1">52-Week Low</td>
                                  <td className="px-2 py-1 text-right">${stockInfo['52WeekLow']}</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1">Beta</td>
                                  <td className="px-2 py-1 text-right">{stockInfo.beta}</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1">Dividend Yield</td>
                                  <td className="px-2 py-1 text-right">{(stockInfo.dividendYield * 100).toFixed(2)}%</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1">P/E Ratio</td>
                                  <td className="px-2 py-1 text-right">{stockInfo.peRatio.toFixed(2)}</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1 font-semibold">ESG Score</td>
                                  <td className="px-2 py-1 text-right text-green-600">{stockInfo.esg}</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1 font-semibold">Environmental Score</td>
                                  <td className="px-2 py-1 text-right text-green-600">{stockInfo.es}</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1 font-semibold">Social Score</td>
                                  <td className="px-2 py-1 text-right text-green-600">{stockInfo.ss}</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1 font-semibold">Governmental Score</td>
                                  <td className="px-2 py-1 text-right text-green-600">{stockInfo.gs}</td>
                                </tr>
                        
                              </tbody>
                            </table>
                          </div>
                      
                          {/* Right Side: Line Chart */}
                          <div className="w-1/2 pl-2" style={{ height: '350px' }}>
                            <Line data={chartData} options={chartOptions} />
                          </div>
                        </div>
                      </div>                                       
                    )}
              </div>
              </div>
              <div className="flex items-center">
                <div className="flex space-x-4">
                  {navigation.map((item) => (
                    <a key={item.name} href={item.href} className={classNames(item.current ? 'text-black' : 'text-gray-500 hover:text-gray-900', 'px-6 py-2 rounded-md text-base font-medium')} aria-current={item.current ? 'page' : undefined}>
                      {item.name}
                    </a>
                  ))}
                </div>
                <img className="hidden sm:block h-16 w-16 rounded-full" src={avatar} alt="" />
              </div>
          </div>
          </div>
        </>
      )}
    </Disclosure>
  );
}
