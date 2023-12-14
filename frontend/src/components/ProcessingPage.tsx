import React, { useEffect, useState, useRef } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { Table, Spin, Button } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { postData } from '../api/apiFunctions';

interface TranslationTuple {
  sourceText: string;
  translatedText: string;
}

interface FileData {
  lines: string[];
  sourceLang: string;
  targetLang: string;
  requestId: string;
}

interface TranslationResponse {
  requestId: string;
  status: boolean;
  results: { [key: string]: string };
}

const ProcessingPage: React.FC = () => {
  const location = useLocation();
  const [data, setData] = useState<TranslationTuple[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const { requestId = '' } = useParams<{ requestId?: string }>();
  const pollingInterval = useRef<number | null>(null);

  // Download feature
  const downloadTxtFile = () => {
    const element = document.createElement("a");
    const file = new Blob([data.map(item => `${item.sourceText}\t${item.translatedText}`).join('\n')], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = "myFile.txt";
    document.body.appendChild(element); // Required for this to work in FireFox
    element.click();
};

  useEffect(() => {
    const { file, sourceLang, targetLang } = location.state as { file: File, sourceLang: string, targetLang: string };

    const reader = new FileReader();

    reader.onload = async (event) => {
      const fileContent = event.target?.result;
      if (typeof fileContent === 'string') {
        const lines = fileContent.split(/\r?\n/).filter(line => line.trim() !== '');
        const uniqueLines = new Set(lines);

        const fileData: FileData = { 
            lines: Array.from(uniqueLines),
            sourceLang, 
            targetLang, 
            requestId 
        };
        
        let currentData = Array.from(uniqueLines).map(line => ({
            sourceText: line, 
            translatedText: ''
        }));

        setData(currentData); // Update state for rendering
        fetchAndPollTranslations(currentData, fileData);
      }
    };

    if (file) {
      reader.readAsText(file);
    }

    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    };
  }, [location.state]);

  const fetchAndPollTranslations = async (currentData: TranslationTuple[], fileData: FileData) => {
    try {
      const initialResponse = await postData('apiv1/translate/request', fileData) as TranslationResponse;
      updateTable(currentData, initialResponse);
  
      // Start polling if not all translations are complete
      if (!initialResponse.status) {
        startPolling(currentData, fileData);
      } else {
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error fetching initial translation:', error);
      setIsLoading(false);
    }
  };
  

  const startPolling = (currentData: TranslationTuple[], fileData: FileData) => {
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
    }
    pollingInterval.current = window.setInterval(async () => {  
      try {
        const response = await postData('apiv1/translate/status', fileData) as TranslationResponse;
        updateTable(currentData, response);
  
        // Stop polling if the response indicates all translations are complete
        console.log(response);
        if (response.status) {
          if (pollingInterval.current) {
            clearInterval(pollingInterval.current);
          }
          setIsLoading(false);
        }
      } catch (error) {
        console.error('Error polling translation:', error);
        if (pollingInterval.current) {
          clearInterval(pollingInterval.current);
        }
        setIsLoading(false);
      }
    }, 5000); // Adjust the interval as needed
  };
  

  const updateTable = (currentData: TranslationTuple[], response: TranslationResponse) => {
    const updatedData = currentData.map(item => {
      if (response.results[item.sourceText]) {
        return { ...item, translatedText: response.results[item.sourceText] };
      }
      return item;
    });
    setData(updatedData);
  };

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
            <Button
                type="primary"
                icon={<DownloadOutlined />}
                onClick={downloadTxtFile}
                style={{ marginBottom: '20px' }}
            >
                Download as TXT
            </Button>
        )}
        <Table dataSource={data} columns={columns} rowKey="sourceText" />
    </div>
  );
};

export default ProcessingPage;



