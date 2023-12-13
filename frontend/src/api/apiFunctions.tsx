import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// POST Request
export const postData = async (url: string, data: any) => {
  const response = await apiClient.post(url, data);
  return response.data;
};

// GET Request
const getData = async (url: string) => {
  const response = await apiClient.get(url);
  return response.data;
};

// PUT Request
const updateData = async (url: string, data: any) => {
  const response = await apiClient.put(url, data);
  return response.data;
};

// DELETE Request
const deleteData = async (url: string) => {
  const response = await apiClient.delete(url);
  return response.data;
};
