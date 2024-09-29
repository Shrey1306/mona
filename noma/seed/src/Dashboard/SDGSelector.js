import React, { useState } from 'react';
import sdg1 from '../art_assets/sdg1.png';
import sdg2 from '../art_assets/sdg2.png';
import sdg3 from '../art_assets/sdg3.png';
import sdg4 from '../art_assets/sdg4.png';
import sdg5 from '../art_assets/sdg5.png';
import sdg6 from '../art_assets/sdg6.png';
import sdg7 from '../art_assets/sdg7.png';
import sdg8 from '../art_assets/sdg8.png';
import sdg9 from '../art_assets/sdg9.png';
import sdg10 from '../art_assets/sdg10.png';
import sdg11 from '../art_assets/sdg11.png';
import sdg12 from '../art_assets/sdg12.png';
import sdg13 from '../art_assets/sdg13.png';
import sdg14 from '../art_assets/sdg14.png';
import sdg15 from '../art_assets/sdg15.png';
import sdg16 from '../art_assets/sdg16.png';
import sdg17 from '../art_assets/sdg17.png';

const sdgs = [
    { id: 1, url: sdg1 },
    { id: 2, url: sdg2 },
    { id: 3, url: sdg3 },
    { id: 4, url: sdg4 },
    { id: 5, url: sdg5 },
    { id: 6, url: sdg6 },
    { id: 7, url: sdg7 },
    { id: 8, url: sdg8 },
    { id: 9, url: sdg9 },
    { id: 10, url: sdg10 },
    { id: 11, url: sdg11 },
    { id: 12, url: sdg12 },
    { id: 13, url: sdg13 },
    { id: 14, url: sdg14 },
    { id: 15, url: sdg15 },
    { id: 16, url: sdg16 },
    { id: 17, url: sdg17 }
];
  

function SDGSelector({ onSelectionChange, selectedSDGs }) {

  const toggleSDG = (id) => {
    const updatedSelectedSDGs = selectedSDGs.includes(id)
      ? selectedSDGs.filter(sdg => sdg !== id)
      : [...selectedSDGs, id];
    onSelectionChange(updatedSelectedSDGs);
  };

  return (
    <div className="flex overflow-x-auto space-x-2 p-2">
      {sdgs.map((sdg) => (
        <SDGTile key={sdg.id} sdg={sdg} toggleSDG={toggleSDG} isSelected={selectedSDGs.includes(sdg.id)} />
      ))}
    </div>
  );
}

function SDGTile({ sdg, toggleSDG, isSelected }) {
  return (
    <div className="relative" onClick={() => toggleSDG(sdg.id)} style={{ cursor: 'pointer' }}>
  <div className="w-56 h-56 rounded-lg" style={{ backgroundImage: `url(${sdg.url})`, backgroundSize: 'contain', backgroundRepeat: 'no-repeat', backgroundPosition: 'center' }}>
    {/* Tile content */}
  </div>
  <input
    id={`checkbox-${sdg.id}`} // Unique ID for the label `for` attribute
    type="checkbox"
    checked={isSelected}
    onChange={() => {}}
    onClick={(e) => e.stopPropagation()}
    className="opacity-0 absolute bottom-2 right-2 h-5 w-5"
  />
  <label htmlFor={`checkbox-${sdg.id}`} className="absolute bottom-2 right-2 h-5 w-5 flex items-center justify-center bg-[#F5F1E3] cursor-pointer rounded-full">
    {isSelected && (
      <svg className="p-1 w-full" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" width="20" height="20" style={{fill: 'white', stroke: 'black', strokeWidth: 2}}>
            <path d="M7.629 14.571L3.142 10.082l1.414-1.414L7.63 11.743l8.115-8.114 1.414 1.414z" />
        </svg>
    )}
  </label>
</div>
  );
}
export default SDGSelector;