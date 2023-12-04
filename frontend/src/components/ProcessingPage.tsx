import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Table, Spin } from 'antd';
import { postData } from '../api/apiFunctions';

interface TranslationTuple {
  sourceText: string;
  translatedText: string;
}

const ProcessingPage: React.FC = () => {
  const location = useLocation();
  const [data, setData] = useState<TranslationTuple[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    const { file, sourceLang, targetLang } = location.state;

    const reader = new FileReader();

    reader.onload = async (event) => {
      const fileContent = event.target?.result;
      if (typeof fileContent === 'string') {
        const lines = fileContent.split(/\r?\n/);
        const fileData = { sourceLang, targetLang, lines };
        setIsLoading(true);

        // Mock Response
        // setTimeout(() => {
        //   // Example of mock data
        //   const mockData = [
        //     { sourceText: 'Hello', translatedText: 'Hola' },
        //     { sourceText: 'World', translatedText: 'Mundo' },
        //     // ... more mock tuples
        //   ];
    
        //   setData(mockData);
        //   setIsLoading(false);
        // }, 2000); // Mocking a 2-second delay

        try {
          const response = await postData('apiv1/translate/upload', fileData);
          console.log(response);
          setData(response); // Assuming response is an array of tuples
          setIsLoading(false);
        } catch (error) {
          console.error('Error processing file:', error);
          setIsLoading(false);
        }
      }
    };

    if (file) {
      reader.readAsText(file);
    }
  }, [location.state]);

  const columns = [
    {
      title: 'Source Text',
      dataIndex: 'sourceText',
      key: 'sourceText',
    },
    {
      title: 'Translated Text',
      dataIndex: 'translatedText',
      key: 'translatedText',
    },
  ];

  return (
    <div>
      <h1>Processing...</h1>
      {isLoading ? (
        <Spin size="large" />
      ) : (
        <Table dataSource={data} columns={columns} rowKey="sourceText" />
      )}
    </div>
  );
};

export default ProcessingPage;


