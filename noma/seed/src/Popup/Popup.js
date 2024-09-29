// Popup.js
import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import Chart from 'chart.js/auto';

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

const Popup = ({ stockSymbol, onClose }) => {
  const [stockInfo, setStockInfo] = useState(null);

  useEffect(() => {
    if (stockSymbol) {
      const fetchData = async () => {
        const data = await fetchStockInfo(stockSymbol);
        setStockInfo(data);
      };
      fetchData();
    }
  }, [stockSymbol]);

  if (!stockInfo) return null;

  // Define chartOptions and chartData inside the component to ensure they have access to stockInfo
  const chartOptions = {
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
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
          display: true, // Adjust based on your preference
        },
        beginAtZero: true
      },
      y: {
        ticks: {
          display: true, // Adjust based on your preference
        },
        beginAtZero: true
      }
    },
    maintainAspectRatio: false
  };

  const chartData = {
    labels: stockInfo.chartData.map((_, index) => `Day ${index + 1}`),
    datasets: [
      {
        label: `${stockInfo.name} Stock Price`,
        data: stockInfo.chartData,
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }
    ]
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full" onClick={onClose}>
      <div className="relative top-20 mx-auto shadow-lg rounded-md bg-white max-w-2xl p-4" onClick={(e) => e.stopPropagation()}>
                      <div className="" onClick={(e) => e.stopPropagation()} > {/* Adjusted width */}
                        <button onClick={onClose} className="absolute top-0 right-0 mt-2 mr-2 text-lg font-semibold">×</button>
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
                                  <td className="px-2 py-1 text-right">{stockInfo.dividendYield == null ? "N/A" : (stockInfo.dividendYield * 100).toFixed(2) + "%"}</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1">P/E Ratio</td>
                                  <td className="px-2 py-1 text-right">{stockInfo.peRatio == null ? "N/A" : stockInfo.peRatio.toFixed(2)}</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1">ESG Score</td>
                                  <td className="px-2 py-1 text-right">{stockInfo.esg == 0 ? "N/A" : stockInfo.esg}</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1">Environmental Score</td>
                                  <td className="px-2 py-1 text-right">{stockInfo.es == 0 ? "N/A" : stockInfo.es}</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1">Social Score</td>
                                  <td className="px-2 py-1 text-right">{stockInfo.ss == 0 ? "N/A" : stockInfo.ss}</td>
                                </tr>
                                <tr>
                                  <td className="px-2 py-1">Governmental Score</td>
                                  <td className="px-2 py-1 text-right">{stockInfo.gs == 0 ? "N/A" : stockInfo.gs}</td>
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
      </div>
    </div>
  );
};

export default Popup;
