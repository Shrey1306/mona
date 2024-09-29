import React from 'react';
import NewsCard from './NewsCard';
import { newsData } from './NewsData';

const NewsFeed = () => {
  return (
    <div className='overflow-y-scroll'>
      {newsData.map((newsItem, index) => (
        <NewsCard
          key={index}
          source={newsItem.source}
          title={newsItem.title}
          description={newsItem.description}
          link={newsItem.link}
          stock = {newsItem.stock}
        />
      ))}
    </div>
  );
};

export default NewsFeed;