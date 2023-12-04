import React from 'react';
import { Select } from 'antd';

const { Option } = Select;

interface LanguageSelectProps {
  languages: Array<{ options: Array<{ value: string; label: string }>; selected: string }>;
  onSelectLanguage: (index: number, value: string) => void;
}

const LanguageSelect: React.FC<LanguageSelectProps> = ({ languages, onSelectLanguage }) => {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px' }}>
      {languages.map((lang, index) => (
        <Select
          key={index}
          style={{ width: 120, margin: '0 10px' }}
          value={lang.selected}
          onChange={(value) => onSelectLanguage(index, value)}
        >
          {lang.options.map((option, i) => (
            <Option key={i} value={option.value}>{option.label}</Option>
          ))}
        </Select>
      ))}
    </div>
  );
};

export default LanguageSelect;
