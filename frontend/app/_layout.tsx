import React from 'react';
import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: {
          backgroundColor: '#3B82F6',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen 
        name="index" 
        options={{
          title: 'POS System',
          headerStyle: {
            backgroundColor: '#3B82F6',
          },
        }} 
      />
      <Stack.Screen 
        name="products" 
        options={{
          title: 'Products',
          presentation: 'card',
        }} 
      />
      <Stack.Screen 
        name="pos" 
        options={{
          title: 'Point of Sale',
          presentation: 'card',
        }} 
      />
      <Stack.Screen 
        name="transactions" 
        options={{
          title: 'Transactions',
          presentation: 'card',
        }} 
      />
      <Stack.Screen 
        name="reports" 
        options={{
          title: 'Reports',
          presentation: 'card',
        }} 
      />
      <Stack.Screen 
        name="add-product" 
        options={{
          title: 'Add Product',
          presentation: 'modal',
        }} 
      />
      <Stack.Screen 
        name="edit-product" 
        options={{
          title: 'Edit Product',
          presentation: 'modal',
        }} 
      />
    </Stack>
  );
}