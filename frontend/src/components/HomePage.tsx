import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LanguageSelect from './LanguageSelect';
import FileUpload from './FileUpload';
import { Button } from 'antd';
import { v4 as uuidv4 } from 'uuid';

interface LanguageOption {
  value: string;
  label: string;
}

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const initialOptions = [
    { value: 'English', label: 'English' },
    { value: 'French', label: 'French' },
    { value: 'Romanian', label: 'Romanian' },
    { value: 'German', label: 'German' }
    // ... other languages
  ];

  const [languages, setLanguages] = useState<Array<{ options: LanguageOption[]; selected: string }>>([
    { options: initialOptions, selected: '' },
    { options: initialOptions, selected: '' }
  ]);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const isReadyToProcess = selectedFile && languages[0].selected && languages[1].selected;

  const handleLanguageSelect = (index: number, value: string) => {
    const newLanguages = languages.map((language, i) => {
      if (i === index) {
        return { ...language, selected: value };
      }
      return {
        ...language,
        options: initialOptions.filter(option => option.value !== value)
      };
    });

    setLanguages(newLanguages);
  };

  const handleFileSelected = (file: File | null) => {
    setSelectedFile(file);
  };

  const handleProcessFile = async () => {
    if (!selectedFile) {
      alert('No file selected!');
      return;
    }
    setIsProcessing(true);

    // Here, you can call the API or perform any action needed
    // and then navigate to the processing page, if necessary
    const requestId = uuidv4();
    navigate(`/processing/${requestId}`, { state: { file: selectedFile, sourceLang: languages[0].selected, targetLang: languages[1].selected } });

    setIsProcessing(false);
  };

  return (
    <div className="HomePage">
      <LanguageSelect 
        languages={languages} 
        onSelectLanguage={handleLanguageSelect}
      />
      <FileUpload onFileSelected={handleFileSelected} />
      <Button
        type="primary"
        onClick={handleProcessFile}
        disabled={!isReadyToProcess}
        loading={isProcessing}
        style={{ marginTop: '20px' }}
      >
        Process File
      </Button>
    </div>
  );
};

export default HomePage;
