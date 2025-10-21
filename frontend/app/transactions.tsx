import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
  SafeAreaView,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Constants from 'expo-constants';

const BACKEND_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

interface TransactionItem {
  product_id: string;
  product_name: string;
  price: number;
  quantity: number;
  total: number;
}

interface Transaction {
  id: string;
  transaction_number: string;
  items: TransactionItem[];
  subtotal: number;
  tax: number;
  discount: number;
  total: number;
  payment_method: string;
  customer_name?: string;
  created_at: string;
  status: string;
}

export default function TransactionsScreen() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchTransactions = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/transactions`);
      if (response.ok) {
        const data = await response.json();
        setTransactions(data);
      } else {
        Alert.alert('Error', 'Failed to load transactions');
      }
    } catch (error) {
      console.error('Error fetching transactions:', error);
      Alert.alert('Error', 'Network error while loading transactions');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchTransactions();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getPaymentMethodIcon = (method: string) => {
    switch (method.toLowerCase()) {
      case 'card':
        return 'card-outline';
      case 'digital':
        return 'phone-portrait-outline';
      default:
        return 'cash-outline';
    }
  };

  const renderTransactionItem = ({ item }: { item: Transaction }) => (
    <View style={styles.transactionCard}>
      <View style={styles.transactionHeader}>
        <View style={styles.transactionInfo}>
          <Text style={styles.transactionNumber}>{item.transaction_number}</Text>
          <Text style={styles.transactionDate}>{formatDate(item.created_at)}</Text>
        </View>
        
        <View style={styles.transactionAmount}>
          <Text style={styles.transactionTotal}>${item.total.toFixed(2)}</Text>
          <View style={styles.paymentMethod}>
            <Ionicons 
              name={getPaymentMethodIcon(item.payment_method) as any} 
              size={16} 
              color="#6B7280" 
            />
            <Text style={styles.paymentMethodText}>{item.payment_method}</Text>
          </View>
        </View>
      </View>

      <View style={styles.itemsContainer}>
        <Text style={styles.itemsHeader}>Items ({item.items.length})</Text>
        {item.items.slice(0, 3).map((transactionItem, index) => (
          <View key={index} style={styles.itemRow}>
            <Text style={styles.itemName} numberOfLines={1}>
              {transactionItem.product_name}
            </Text>
            <Text style={styles.itemDetails}>
              {transactionItem.quantity}x ${transactionItem.price.toFixed(2)}
            </Text>
          </View>
        ))}
        {item.items.length > 3 && (
          <Text style={styles.moreItemsText}>
            +{item.items.length - 3} more items
          </Text>
        )}
      </View>

      <View style={styles.transactionFooter}>
        <View style={[
          styles.statusBadge,
          item.status === 'completed' ? styles.statusCompleted : styles.statusPending
        ]}>
          <Text style={[
            styles.statusText,
            item.status === 'completed' ? styles.statusTextCompleted : styles.statusTextPending
          ]}>
            {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
          </Text>
        </View>
        
        <TouchableOpacity
          style={styles.viewButton}
          onPress={() => showTransactionDetails(item)}
        >
          <Text style={styles.viewButtonText}>View Details</Text>
          <Ionicons name="chevron-forward" size={16} color="#3B82F6" />
        </TouchableOpacity>
      </View>
    </View>
  );

  const showTransactionDetails = (transaction: Transaction) => {
    const itemsList = transaction.items
      .map(item => `${item.product_name} (${item.quantity}x $${item.price.toFixed(2)})`)
      .join('\n');

    Alert.alert(
      `Transaction ${transaction.transaction_number}`,
      `Date: ${formatDate(transaction.created_at)}\n\nItems:\n${itemsList}\n\nSubtotal: $${transaction.subtotal.toFixed(2)}\nTax: $${transaction.tax.toFixed(2)}\nDiscount: $${transaction.discount.toFixed(2)}\nTotal: $${transaction.total.toFixed(2)}\n\nPayment: ${transaction.payment_method}${transaction.customer_name ? `\nCustomer: ${transaction.customer_name}` : ''}`,
      [{ text: 'OK' }]
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
        <Text style={styles.loadingText}>Loading transactions...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Summary Cards */}
      <View style={styles.summaryContainer}>
        <View style={styles.summaryCard}>
          <Ionicons name="receipt-outline" size={24} color="#3B82F6" />
          <Text style={styles.summaryValue}>{transactions.length}</Text>
          <Text style={styles.summaryLabel}>Total Transactions</Text>
        </View>
        
        <View style={styles.summaryCard}>
          <Ionicons name="cash-outline" size={24} color="#10B981" />
          <Text style={styles.summaryValue}>
            ${transactions.reduce((sum, t) => sum + t.total, 0).toFixed(2)}
          </Text>
          <Text style={styles.summaryLabel}>Total Revenue</Text>
        </View>
      </View>

      {/* Transactions List */}
      <FlatList
        data={transactions}
        renderItem={renderTransactionItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="receipt-outline" size={64} color="#9CA3AF" />
            <Text style={styles.emptyText}>No transactions yet</Text>
            <Text style={styles.emptySubtext}>
              Start selling products to see transaction history
            </Text>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6B7280',
  },
  summaryContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  summaryCard: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  summaryValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 8,
    marginBottom: 4,
  },
  summaryLabel: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
  },
  listContainer: {
    padding: 16,
    paddingTop: 0,
  },
  transactionCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  transactionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  transactionInfo: {
    flex: 1,
  },
  transactionNumber: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 4,
  },
  transactionDate: {
    fontSize: 14,
    color: '#6B7280',
  },
  transactionAmount: {
    alignItems: 'flex-end',
  },
  transactionTotal: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#059669',
    marginBottom: 4,
  },
  paymentMethod: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  paymentMethodText: {
    fontSize: 12,
    color: '#6B7280',
    textTransform: 'capitalize',
  },
  itemsContainer: {
    marginBottom: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
  },
  itemsHeader: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  itemRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  itemName: {
    flex: 1,
    fontSize: 14,
    color: '#6B7280',
    marginRight: 8,
  },
  itemDetails: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  moreItemsText: {
    fontSize: 12,
    color: '#9CA3AF',
    fontStyle: 'italic',
    marginTop: 4,
  },
  transactionFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusCompleted: {
    backgroundColor: '#D1FAE5',
  },
  statusPending: {
    backgroundColor: '#FEF3C7',
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  statusTextCompleted: {
    color: '#065F46',
  },
  statusTextPending: {
    color: '#92400E',
  },
  viewButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  viewButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#3B82F6',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#4B5563',
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    textAlign: 'center',
  },
});