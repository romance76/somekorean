import { ref } from 'vue';
import axios from 'axios';

export function usePokerWallet() {
  const wallet = ref(null);
  const stats = ref(null);
  const leaderboard = ref([]);
  const transactions = ref([]);
  const loading = ref(false);
  const error = ref(null);

  async function fetchWallet() {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await axios.get('/api/poker/wallet');
      if (data.success) {
        wallet.value = data.data;
      }
    } catch (e) {
      error.value = e.response?.data?.message || e.message;
    } finally {
      loading.value = false;
    }
  }

  async function deposit(amount) {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await axios.post('/api/poker/wallet/deposit', { amount });
      if (data.success) {
        // Update wallet balance from response
        if (wallet.value) {
          wallet.value = { ...wallet.value, chips_balance: data.data.chips_balance, points: data.data.points };
        } else {
          wallet.value = data.data;
        }
        return data;
      }
    } catch (e) {
      error.value = e.response?.data?.message || e.message;
    } finally {
      loading.value = false;
    }
  }

  async function withdraw(amount) {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await axios.post('/api/poker/wallet/withdraw', { amount });
      if (data.success) {
        if (wallet.value) {
          wallet.value = { ...wallet.value, chips_balance: data.data.chips_balance, points: data.data.points };
        } else {
          wallet.value = data.data;
        }
        return data;
      }
    } catch (e) {
      error.value = e.response?.data?.message || e.message;
    } finally {
      loading.value = false;
    }
  }

  async function fetchTransactions(page = 1) {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await axios.get('/api/poker/wallet/transactions', { params: { page } });
      if (data.success) {
        transactions.value = data.data;
      }
    } catch (e) {
      error.value = e.response?.data?.message || e.message;
    } finally {
      loading.value = false;
    }
  }

  async function saveGame(gameData) {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await axios.post('/api/poker/games', gameData);
      if (data.success) {
        return data.data;
      }
    } catch (e) {
      error.value = e.response?.data?.message || e.message;
    } finally {
      loading.value = false;
    }
  }

  async function fetchStats() {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await axios.get('/api/poker/stats');
      if (data.success) {
        stats.value = data.data;
      }
    } catch (e) {
      error.value = e.response?.data?.message || e.message;
    } finally {
      loading.value = false;
    }
  }

  async function fetchLeaderboard() {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await axios.get('/api/poker/leaderboard');
      if (data.success) {
        leaderboard.value = data.data;
      }
    } catch (e) {
      error.value = e.response?.data?.message || e.message;
    } finally {
      loading.value = false;
    }
  }

  async function fetchHistory(page = 1) {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await axios.get('/api/poker/history', { params: { page } });
      if (data.success) {
        return data.data;
      }
    } catch (e) {
      error.value = e.response?.data?.message || e.message;
    } finally {
      loading.value = false;
    }
  }

  return {
    wallet,
    stats,
    leaderboard,
    transactions,
    loading,
    error,
    fetchWallet,
    deposit,
    withdraw,
    fetchTransactions,
    saveGame,
    fetchStats,
    fetchLeaderboard,
    fetchHistory,
  };
}
