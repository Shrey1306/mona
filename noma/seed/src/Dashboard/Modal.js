import React from 'react';

const Modal = ({ show, children }) => {
  if (!show) {
    return null;
  }

  return (
      <div className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-75 flex items-center justify-center z-50">
        <div className="bg-[#f4e9e1] w-11/12 md:w-5/6 lg:w-2/3 xl:w-2/3 h-3/4 overflow-auto rounded-2xl">
          {children}
        </div>
      </div>
    );
};

export default Modal;
