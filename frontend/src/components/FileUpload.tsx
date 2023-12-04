import React, { useState } from 'react';
import { Upload, message, Button } from 'antd';
import { InboxOutlined } from '@ant-design/icons';  // Import the icon here

const { Dragger } = Upload;

interface FileUploadProps {
  onFileSelected: (file: File | null) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileSelected }) => {
  const [fileList, setFileList] = useState<any[]>([]);

  const props = {
    name: 'file',
    multiple: false,
    accept: '.txt',
    fileList,
    beforeUpload: (file: File) => {
      setFileList([file]);
      onFileSelected(file);
      return false;
    },
    onRemove: () => {
      setFileList([]);
      onFileSelected(null);
    },
    onChange(info: any) {
      if (info.file.status === 'removed') {
        setFileList([]);
      }
    },
  };

  return (
    <Dragger {...props} style={{ padding: '20px', height: '200px' }}>
      <p className="ant-upload-drag-icon">
        <InboxOutlined />  {/* Using the imported icon */}
      </p>
      <p className="ant-upload-text">Click or drag file to this area to upload</p>
      <p className="ant-upload-hint">
        Support for a single .txt file upload.
      </p>
    </Dragger>
  );
};

export default FileUpload;



