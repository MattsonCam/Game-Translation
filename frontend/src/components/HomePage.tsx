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
  const [languages, setLanguages] = useState<Array<{ options: LanguageOption[]; selected: string }>>([
    { options: [{ value: 'en', label: 'English' }, /* ... other languages */], selected: '' },
    { options: [{ value: 'es', label: 'Spanish' }, /* ... other languages */], selected: '' }
  ]);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const handleLanguageSelect = (index: number, value: string) => {
    const newLanguages = [...languages];
    newLanguages[index].selected = value;
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
        disabled={!selectedFile}
        loading={isProcessing}
        style={{ marginTop: '20px' }}
      >
        Process File
      </Button>
    </div>
  );
};

export default HomePage;
