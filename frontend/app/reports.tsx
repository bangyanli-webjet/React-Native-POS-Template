import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  SafeAreaView,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Constants from 'expo-constants';

const BACKEND_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

interface DashboardStats {
  total_products: number;
  total_transactions: number;
  today_revenue: number;
  today_transactions: number;
  low_stock_count: number;
}

export default function ReportsScreen() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/dashboard/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        Alert.alert('Error', 'Failed to load statistics');
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
      Alert.alert('Error', 'Network error while loading statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
        <Text style={styles.loadingText}>Loading reports...</Text>
      </View>
    );
  }

  if (!stats) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="alert-circle-outline" size={48} color="#EF4444" />
        <Text style={styles.errorText}>Failed to load statistics</Text>
        <TouchableOpacity style={styles.retryButton} onPress={fetchStats}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const statCards = [
    {
      title: 'Today\'s Revenue',
      value: `$${stats.today_revenue.toFixed(2)}`,
      icon: 'cash-outline',
      color: '#10B981',
      bgColor: '#D1FAE5',
    },
    {
      title: 'Today\'s Orders',
      value: stats.today_transactions.toString(),
      icon: 'receipt-outline',
      color: '#3B82F6',
      bgColor: '#DBEAFE',
    },
    {
      title: 'Total Products',
      value: stats.total_products.toString(),
      icon: 'cube-outline',
      color: '#8B5CF6',
      bgColor: '#EDE9FE',
    },
    {
      title: 'Total Transactions',
      value: stats.total_transactions.toString(),
      icon: 'trending-up-outline',
      color: '#F59E0B',
      bgColor: '#FEF3C7',
    },
  ];

  const alertCards = [
    {
      title: 'Low Stock Alert',
      value: `${stats.low_stock_count} products`,
      description: 'Products with less than 10 items in stock',
      icon: 'warning-outline',
      color: '#EF4444',
      bgColor: '#FEE2E2',
      priority: stats.low_stock_count > 0 ? 'high' : 'normal',
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Business Reports</Text>
          <Text style={styles.headerSubtitle}>Overview of your store performance</Text>
        </View>

        {/* Main Statistics */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Today's Performance</Text>
          <View style={styles.statsGrid}>
            {statCards.map((card, index) => (
              <View key={index} style={styles.statCard}>
                <View style={[styles.statIcon, { backgroundColor: card.bgColor }]}>
                  <Ionicons name={card.icon as any} size={24} color={card.color} />
                </View>
                <Text style={styles.statValue}>{card.value}</Text>
                <Text style={styles.statTitle}>{card.title}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Alerts Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Alerts & Notifications</Text>
          {alertCards.map((alert, index) => (
            <View 
              key={index} 
              style={[
                styles.alertCard,
                alert.priority === 'high' ? styles.alertCardHigh : null
              ]}
            >
              <View style={[styles.alertIcon, { backgroundColor: alert.bgColor }]}>
                <Ionicons name={alert.icon as any} size={20} color={alert.color} />
              </View>
              <View style={styles.alertContent}>
                <Text style={styles.alertTitle}>{alert.title}</Text>
                <Text style={styles.alertValue}>{alert.value}</Text>
                <Text style={styles.alertDescription}>{alert.description}</Text>
              </View>
              {alert.priority === 'high' && (
                <View style={styles.priorityBadge}>
                  <Text style={styles.priorityText}>!</Text>
                </View>
              )}
            </View>
          ))}
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionsGrid}>
            <TouchableOpacity style={styles.actionCard} onPress={fetchStats}>
              <Ionicons name="refresh-outline" size={24} color="#3B82F6" />
              <Text style={styles.actionTitle}>Refresh Data</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.actionCard}
              onPress={() => Alert.alert('Feature Coming Soon', 'Export functionality will be available in the next update!')}
            >
              <Ionicons name="download-outline" size={24} color="#10B981" />
              <Text style={styles.actionTitle}>Export Report</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Performance Insights */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Insights</Text>
          <View style={styles.insightsContainer}>
            {stats.today_revenue > 0 ? (
              <View style={styles.insightCard}>
                <Ionicons name="trending-up" size={20} color="#10B981" />
                <Text style={styles.insightText}>
                  Great! You've made ${stats.today_revenue.toFixed(2)} in sales today
                </Text>
              </View>
            ) : (
              <View style={styles.insightCard}>
                <Ionicons name="information-circle" size={20} color="#3B82F6" />
                <Text style={styles.insightText}>
                  No sales recorded today. Consider promoting your products!
                </Text>
              </View>
            )}
            
            {stats.low_stock_count > 0 && (
              <View style={[styles.insightCard, styles.warningInsight]}>
                <Ionicons name="warning" size={20} color="#F59E0B" />
                <Text style={styles.insightText}>
                  {stats.low_stock_count} products are running low on stock. Restock soon!
                </Text>
              </View>
            )}

            {stats.total_products === 0 && (
              <View style={styles.insightCard}>
                <Ionicons name="add-circle" size={20} color="#8B5CF6" />
                <Text style={styles.insightText}>
                  Start by adding products to your inventory to begin selling
                </Text>
              </View>
            )}
          </View>
        </View>
      </ScrollView>
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
    padding: 20,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6B7280',
  },
  errorText: {
    fontSize: 16,
    color: '#EF4444',
    marginTop: 16,
    marginBottom: 20,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  scrollContent: {
    padding: 16,
  },
  header: {
    marginBottom: 24,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#6B7280',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  statCard: {
    width: '48%',
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
  statIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4,
  },
  statTitle: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
  },
  alertCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 3,
  },
  alertCardHigh: {
    borderLeftWidth: 4,
    borderLeftColor: '#EF4444',
  },
  alertIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  alertContent: {
    flex: 1,
  },
  alertTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 2,
  },
  alertValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 4,
  },
  alertDescription: {
    fontSize: 12,
    color: '#6B7280',
  },
  priorityBadge: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#EF4444',
    alignItems: 'center',
    justifyContent: 'center',
  },
  priorityText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  actionsGrid: {
    flexDirection: 'row',
    gap: 12,
  },
  actionCard: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
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
  actionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginTop: 8,
    textAlign: 'center',
  },
  insightsContainer: {
    gap: 12,
  },
  insightCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 3,
  },
  warningInsight: {
    backgroundColor: '#FFFBEB',
    borderColor: '#F59E0B',
    borderWidth: 1,
  },
  insightText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    marginLeft: 12,
    lineHeight: 20,
  },
});