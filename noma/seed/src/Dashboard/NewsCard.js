// Assuming Popup.js is in the same directory
import Popup from '../Popup/Popup.js';
import React, { useState } from 'react';

const NewsCard = ({ source, title, description, link, stock }) => {
  const [showPopup, setShowPopup] = useState(false);

  return (
    <div className="w-full rounded overflow-hidden shadow-lg mb-2 mt-2 bg-white">
      <div className="px-6 py-4">
        <div className="font-semibold text-xs mb-2">{source}</div>
        <div className="font-weight-600 text-xl mb-2">{title}</div>
        <p className="text-gray-700 text-base">
          {description}
        </p>
      </div>
      <div className="px-6 pb-4 flex items-center justify-between">
        <button type="button" onClick={() => navigateLink(link)} className="text-white text-sm py-3 px-4 rounded-lg bg-[#142629] hover:bg-[#142629]/[0.8]">
          Read More
        </button>
        <p onClick={() => setShowPopup(true)}>
          {stock} <span className="text-stone-300">▶</span>
        </p>
      </div>
      {showPopup && <Popup stockSymbol={stock} onClose={() => setShowPopup(false)} />}
    </div>
  );
};

const navigateLink = (link) => {
  window.location.href = link;
};

export default NewsCard;
