import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, TextInput, View, ScrollView, Alert, TouchableOpacity, Platform, KeyboardAvoidingView } from 'react-native';
import { useFonts, Lato_400Regular, Lato_700Bold } from '@expo-google-fonts/lato';
import * as SplashScreen from 'expo-splash-screen';

SplashScreen.preventAutoHideAsync();

const API_BASE_URL =
  Platform.OS === 'android'
    ? 'http://10.0.2.2:8000' // Android emulator loopback
    : 'http://127.0.0.1:8000'; // iOS simulator or local machine

export default function App() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [responseData, setResponseData] = useState<any>(null);

  let [fontsLoaded] = useFonts({
    Lato_400Regular,
    Lato_700Bold,
  });

  useEffect(() => {
    async function prepare() {
      try {
        console.log("Preparing app...");
        // Perform any async tasks here
      } catch (e) {
        console.warn("Error during preparation:", e);
      } finally {
        try {
          await SplashScreen.hideAsync();
        } catch (e) {
          console.warn("Error hiding splash screen:", e);
        }
      }
    }

    if (fontsLoaded) {
      prepare();
    }
  }, [fontsLoaded]);

  const testBackendConnection = async () => {
    try {
      console.log('Testing backend connection...');
      const res = await fetch(`${API_BASE_URL}/health`, { method: 'GET' });
      if (!res.ok) {
        throw new Error(`Backend health check failed: ${res.status}`);
      }
      console.log('Backend connection successful');
    } catch (error) {
      console.error('Backend connection error:', error);
      Alert.alert(
        'Error',
        'Unable to connect to the backend. Please ensure the backend is running and accessible.'
      );
    }
  };

  useEffect(() => {
    testBackendConnection(); // Test backend connection on app load
  }, []);

  if (!fontsLoaded) {
    return null; // Return null while fonts are loading
  }

  const callApi = async (endpoint: string) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10-second timeout

    try {
      console.log('Calling API:', `${API_BASE_URL}${endpoint}`);
      console.log('Request Body:', { email, password });

      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ email, password }).toString(),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      console.log('Response Status:', res.status);

      if (!res.ok) {
        const errorText = await res.text(); // Capture error response text
        console.error(`Backend Error Response: ${errorText}`); // Log the backend error
        throw new Error(`Error: ${res.status} - ${errorText}`);
      }

      const data = await res.json();
      console.log('Response Data:', data);

      const cleanedData = cleanData(data);
      setResponseData(cleanedData);
    } catch (error) {
      clearTimeout(timeoutId);
      console.error('Network Error:', error); // Log network errors
      if (error instanceof Error) {
        if (error.message === 'Network request failed') {
          Alert.alert(
            'Error',
            'Unable to connect to the server. Please check your network or server status.'
          );
        } else if (error.name === 'AbortError') {
          Alert.alert('Error', 'Request timed out. Please try again.');
        } else {
          Alert.alert('Error', error.message);
        }
      } else {
        Alert.alert('Error', 'An unexpected error occurred. Please try again later.');
      }
    }
  };

  const cleanData = (data: any) => {
    // Example of cleaning and organizing data
    if (typeof data === 'object' && data !== null) {
      return JSON.stringify(data, null, 2); // Pretty-print JSON
    }
    return data;
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        contentContainerStyle={styles.container}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.title}>Tabroom Scraper</Text>
        <TextInput
          style={styles.input}
          placeholder="Email"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />
        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.button} onPress={() => callApi('/dashboard/')}>
            <Text style={styles.buttonText}>Get Dashboard</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.button} onPress={() => callApi('/nsda/')}>
            <Text style={styles.buttonText}>Get NSDA Points</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.button} onPress={() => callApi('/paradigm/')}>
            <Text style={styles.buttonText}>Get Paradigm</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.button} onPress={() => callApi('/account/')}>
            <Text style={styles.buttonText}>Get Account Info</Text>
          </TouchableOpacity>
        </View>
        {responseData ? (
          <View style={styles.responseContainer}>
            <Text style={styles.responseTitle}>Response:</Text>
            <Text style={styles.response}>{responseData}</Text>
          </View>
        ) : null}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: '#0f0f10',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    fontFamily: 'Lato_700Bold',
    color: '#f3f4f6',
    marginBottom: 30,
    marginTop: 50,
  },
  input: {
    width: '100%',
    height: 50,
    borderColor: '#1f2937',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 15,
    marginBottom: 15,
    backgroundColor: '#111827',
    color: '#f3f4f6',
    fontFamily: 'Lato_400Regular',
  },
  buttonContainer: {
    width: '100%',
    marginVertical: 20,
  },
  button: {
    backgroundColor: '#2563eb',
    paddingVertical: 15,
    borderRadius: 8,
    marginBottom: 10,
    alignItems: 'center',
  },
  buttonText: {
    color: '#f3f4f6',
    fontSize: 16,
    fontWeight: '600',
    fontFamily: 'Lato_700Bold',
  },
  responseContainer: {
    marginTop: 20,
    width: '100%',
    backgroundColor: '#1f2937',
    padding: 15,
    borderRadius: 15,
  },
  responseTitle: {
    fontSize: 18,
    fontWeight: '700',
    fontFamily: 'Lato_700Bold',
    color: '#f3f4f6',
    marginBottom: 10,
  },
  response: {
    fontSize: 14,
    color: '#d1d5db',
    fontFamily: 'Lato_400Regular',
  },
});
