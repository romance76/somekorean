<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10">
      <div class="max-w-4xl mx-auto px-4 py-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-2xl">🎵</span>
            <h1 class="text-xl font-bold text-gray-900 dark:text-white">음악듣기</h1>
          </div>
          <button v-if="authStore.isLoggedIn" @click="openMyPlaylists"
            class="flex items-center gap-1 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-full text-sm font-medium transition-colors">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"/></svg>
            내 뮤직함
          </button>
        </div>

        <!-- Category Tabs -->
        <div class="flex gap-2 mt-3 overflow-x-auto pb-1 scrollbar-hide">
          <button v-for="cat in categories" :key="cat.id"
            @click="selectCategory(cat)"
            :class="['flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium transition-colors',
              selectedCat && selectedCat.id === cat.id
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600']">
            {{ cat.icon }} {{ cat.name }}
            <span class="ml-1 text-xs opacity-70">({{ cat.tracks_count }})</span>
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-4 py-4 flex gap-4">
      <!-- Track List -->
      <div class="flex-1">
        <div v-if="loading" class="flex justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </div>
        <div v-else-if="!selectedCat" class="text-center py-12 text-gray-500 dark:text-gray-400">
          카테고리를 선택해주세요
        </div>
        <div v-else-if="tracks.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
          <div class="text-4xl mb-3">🎵</div>
          <p>아직 음악이 없습니다</p>
        </div>
        <div v-else class="space-y-2">
          <div v-for="(track, index) in tracks" :key="track.id"
            @click="playTrack(track)"
            :class="['flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all',
              currentTrack && currentTrack.id === track.id
                ? 'bg-purple-50 dark:bg-purple-900/30 border border-purple-200 dark:border-purple-700'
                : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-100 dark:border-gray-700']">
            <!-- Thumbnail -->
            <div class="relative flex-shrink-0 w-16 h-12 rounded-lg overflow-hidden bg-gray-200">
              <img v-if="track.thumbnail" :src="track.thumbnail" :alt="track.title" class="w-full h-full object-cover">
              <div v-else class="w-full h-full flex items-center justify-center text-gray-400 text-xl">🎵</div>
              <div v-if="currentTrack && currentTrack.id === track.id && isPlaying"
                class="absolute inset-0 bg-purple-600/70 flex items-center justify-center">
                <div class="flex gap-0.5 items-end h-5">
                  <div v-for="i in 4" :key="i" class="w-1 bg-white rounded-full animate-music-bar" :style="'animation-delay:' + (i * 0.1) + 's'"></div>
                </div>
              </div>
              <div v-else-if="currentTrack && currentTrack.id === track.id"
                class="absolute inset-0 bg-purple-600/70 flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg>
              </div>
            </div>
            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="font-medium text-gray-900 dark:text-white truncate text-sm">{{ track.title }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">{{ track.artist || '아티스트 정보 없음' }}</div>
              <div class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">재생 {{ track.play_count }}회</div>
            </div>
            <div class="flex-shrink-0 text-sm font-medium text-gray-400 dark:text-gray-500 w-6 text-right">{{ index + 1 }}</div>
          </div>
        </div>
      </div>

      <!-- Player Sidebar (desktop) -->
      <div v-if="currentTrack" class="hidden lg:block w-80 flex-shrink-0">
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden sticky top-24">
          <div class="relative pt-[56.25%]">
            <iframe :src="'https://www.youtube.com/embed/' + currentTrack.youtube_id + '?autoplay=1&rel=0'"
              class="absolute inset-0 w-full h-full"
              frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
          </div>
          <div class="p-4">
            <div class="font-bold text-gray-900 dark:text-white text-sm leading-snug">{{ currentTrack.title }}</div>
            <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ currentTrack.artist }}</div>
            <div class="flex items-center justify-between mt-4">
              <button @click="prevTrack" class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M8.445 14.832A1 1 0 0010 14v-2.798l5.445 3.63A1 1 0 0017 14V6a1 1 0 00-1.555-.832L10 8.798V6a1 1 0 00-1.555-.832l-6 4a1 1 0 000 1.664l6 4z"/></svg>
              </button>
              <button @click="togglePlay" class="p-3 bg-purple-600 hover:bg-purple-700 text-white rounded-full">
                <svg v-if="isPlaying" class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
                <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg>
              </button>
              <button @click="nextTrack" class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M4.555 5.168A1 1 0 003 6v8a1 1 0 001.555.832L10 11.202V14a1 1 0 001.555.832l6-4a1 1 0 000-1.664l-6-4A1 1 0 0010 6v2.798L4.555 5.168z"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Player (fixed bottom) -->
    <div v-if="currentTrack" class="lg:hidden fixed bottom-16 left-0 right-0 z-40 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 shadow-xl">
      <div class="flex items-center gap-3 px-4 py-2">
        <img v-if="currentTrack.thumbnail" :src="currentTrack.thumbnail" class="w-10 h-10 rounded-lg object-cover flex-shrink-0">
        <div class="flex-1 min-w-0">
          <div class="font-medium text-gray-900 dark:text-white text-sm truncate">{{ currentTrack.title }}</div>
          <div class="text-xs text-gray-500 truncate">{{ currentTrack.artist }}</div>
        </div>
        <div class="flex items-center gap-2">
          <button @click="prevTrack" class="p-1.5 text-gray-600 dark:text-gray-400">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M8.445 14.832A1 1 0 0010 14v-2.798l5.445 3.63A1 1 0 0017 14V6a1 1 0 00-1.555-.832L10 8.798V6a1 1 0 00-1.555-.832l-6 4a1 1 0 000 1.664l6 4z"/></svg>
          </button>
          <button @click="togglePlay" class="p-1.5 bg-purple-600 text-white rounded-full">
            <svg v-if="isPlaying" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
            <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg>
          </button>
          <button @click="nextTrack" class="p-1.5 text-gray-600 dark:text-gray-400">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M4.555 5.168A1 1 0 003 6v8a1 1 0 001.555.832L10 11.202V14a1 1 0 001.555.832l6-4a1 1 0 000-1.664l-6-4A1 1 0 0010 6v2.798L4.555 5.168z"/></svg>
          </button>
        </div>
        <button @click="showMobilePlayer = true" class="p-1.5 text-purple-600">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd"/></svg>
        </button>
      </div>
    </div>

    <!-- Mobile Full Player Modal -->
    <div v-if="showMobilePlayer && currentTrack" class="lg:hidden fixed inset-0 z-50 bg-gray-900/95 flex flex-col">
      <div class="flex items-center justify-between p-4">
        <button @click="showMobilePlayer = false" class="text-white p-2">
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
        </button>
        <span class="text-white font-medium">지금 재생 중</span>
        <div class="w-10"></div>
      </div>
      <div class="flex-1 flex flex-col items-center justify-center px-8">
        <div class="relative w-full rounded-2xl overflow-hidden mb-8" style="padding-top:56.25%">
          <iframe :src="'https://www.youtube.com/embed/' + currentTrack.youtube_id + '?autoplay=1&rel=0'"
            class="absolute inset-0 w-full h-full"
            frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </div>
        <div class="text-center mb-8">
          <div class="text-white text-xl font-bold">{{ currentTrack.title }}</div>
          <div class="text-gray-400 mt-1">{{ currentTrack.artist }}</div>
        </div>
        <div class="flex items-center gap-8">
          <button @click="prevTrack" class="text-white p-3">
            <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20"><path d="M8.445 14.832A1 1 0 0010 14v-2.798l5.445 3.63A1 1 0 0017 14V6a1 1 0 00-1.555-.832L10 8.798V6a1 1 0 00-1.555-.832l-6 4a1 1 0 000 1.664l6 4z"/></svg>
          </button>
          <button @click="togglePlay" class="p-5 bg-purple-600 text-white rounded-full">
            <svg v-if="isPlaying" class="w-10 h-10" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
            <svg v-else class="w-10 h-10" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg>
          </button>
          <button @click="nextTrack" class="text-white p-3">
            <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20"><path d="M4.555 5.168A1 1 0 003 6v8a1 1 0 001.555.832L10 11.202V14a1 1 0 001.555.832l6-4a1 1 0 000-1.664l-6-4A1 1 0 0010 6v2.798L4.555 5.168z"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- My Playlists Modal -->
    <div v-if="showMyPlaylists" class="fixed inset-0 z-50 bg-black/50 flex items-end sm:items-center justify-center">
      <div class="bg-white dark:bg-gray-800 w-full sm:max-w-lg sm:rounded-2xl rounded-t-2xl max-h-[80vh] flex flex-col">
        <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">내 뮤직함</h2>
          <button @click="showMyPlaylists = false" class="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-4">
          <button @click="showCreatePlaylist = true" class="w-full flex items-center gap-3 p-3 border-2 border-dashed border-purple-300 dark:border-purple-700 rounded-xl text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 mb-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            새 플레이리스트 만들기
          </button>
          <div v-if="playlistsLoading" class="text-center py-8 text-gray-500">불러오는 중...</div>
          <div v-else-if="playlists.length === 0" class="text-center py-8 text-gray-500">
            <div class="text-3xl mb-2">🎵</div>
            <p>아직 플레이리스트가 없어요</p>
          </div>
          <div v-else class="space-y-2">
            <div v-for="pl in playlists" :key="pl.id"
              class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer"
              @click="openPlaylist(pl)">
              <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center text-xl flex-shrink-0">🎵</div>
              <div class="flex-1 min-w-0">
                <div class="font-medium text-gray-900 dark:text-white truncate">{{ pl.name }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ pl.tracks_count }}곡</div>
              </div>
              <button @click.stop="deletePlaylist(pl.id)" class="p-1.5 text-red-400 hover:text-red-600">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Playlist Modal -->
    <div v-if="showCreatePlaylist" class="fixed inset-0 z-[60] bg-black/50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-sm p-6">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">새 플레이리스트</h3>
        <input v-model="newPlaylistName" type="text" placeholder="플레이리스트 이름" maxlength="100"
          class="w-full border border-gray-300 dark:border-gray-600 rounded-xl px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white mb-3 focus:outline-none focus:ring-2 focus:ring-purple-500">
        <textarea v-model="newPlaylistDesc" placeholder="설명 (선택)" rows="2" maxlength="500"
          class="w-full border border-gray-300 dark:border-gray-600 rounded-xl px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white mb-4 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"></textarea>
        <div class="flex gap-2">
          <button @click="showCreatePlaylist = false" class="flex-1 py-2.5 border border-gray-300 dark:border-gray-600 rounded-xl text-gray-700 dark:text-gray-300">취소</button>
          <button @click="createPlaylist" :disabled="!newPlaylistName.trim()" class="flex-1 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-xl font-medium">만들기</button>
        </div>
      </div>
    </div>

    <!-- Playlist Detail Modal -->
    <div v-if="activePlaylist" class="fixed inset-0 z-[60] bg-black/50 flex items-end sm:items-center justify-center">
      <div class="bg-white dark:bg-gray-800 w-full sm:max-w-lg sm:rounded-2xl rounded-t-2xl max-h-[85vh] flex flex-col">
        <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 class="text-lg font-bold text-gray-900 dark:text-white">{{ activePlaylist.name }}</h2>
            <p class="text-sm text-gray-500">{{ activePlaylist.tracks ? activePlaylist.tracks.length : 0 }}곡</p>
          </div>
          <button @click="activePlaylist = null" class="p-2 text-gray-500">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-4">
          <div class="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-3 mb-4">
            <h4 class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-2">+ 음악 추가</h4>
            <input v-model="addTrackUrl" type="text" placeholder="YouTube URL (https://youtube.com/watch?v=...)" maxlength="500"
              class="w-full border border-purple-200 dark:border-purple-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-purple-500">
            <button @click="addTrackToPlaylist" :disabled="!addTrackUrl.trim()" class="w-full py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium">추가하기</button>
          </div>
          <div v-if="!activePlaylist.tracks || activePlaylist.tracks.length === 0" class="text-center py-6 text-gray-500 text-sm">아직 음악이 없어요. 위에서 추가해보세요!</div>
          <div v-else class="space-y-2">
            <div v-for="track in activePlaylist.tracks" :key="track.id"
              class="flex items-center gap-3 p-2.5 bg-gray-50 dark:bg-gray-700 rounded-xl">
              <img v-if="track.thumbnail" :src="track.thumbnail" class="w-12 h-9 rounded-lg object-cover flex-shrink-0">
              <div v-else class="w-12 h-9 bg-gray-200 dark:bg-gray-600 rounded-lg flex items-center justify-center text-gray-400 flex-shrink-0">🎵</div>
              <div class="flex-1 min-w-0">
                <div class="font-medium text-gray-900 dark:text-white text-sm truncate">{{ track.title }}</div>
                <div class="text-xs text-gray-500">{{ track.artist || '' }}</div>
              </div>
              <button @click="playUserTrack(track)" class="p-1.5 text-purple-600 hover:text-purple-700">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg>
              </button>
              <button @click="removeTrack(activePlaylist.id, track.id)" class="p-1.5 text-red-400 hover:text-red-600">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const categories = ref([])
const selectedCat = ref(null)
const tracks = ref([])
const loading = ref(false)
const currentTrack = ref(null)
const isPlaying = ref(false)
const showMobilePlayer = ref(false)

const showMyPlaylists = ref(false)
const playlists = ref([])
const playlistsLoading = ref(false)
const showCreatePlaylist = ref(false)
const newPlaylistName = ref('')
const newPlaylistDesc = ref('')
const activePlaylist = ref(null)

const addTrackUrl = ref('')

onMounted(async () => {
  await loadCategories()
})

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/music/categories')
    categories.value = data
    if (data.length > 0) await selectCategory(data[0])
  } catch (e) { console.error(e) }
}

async function selectCategory(cat) {
  selectedCat.value = cat
  loading.value = true
  try {
    const { data } = await axios.get('/api/music/categories/' + cat.id + '/tracks')
    tracks.value = data.tracks
  } catch (e) { tracks.value = [] }
  loading.value = false
}

async function playTrack(track) {
  currentTrack.value = track
  isPlaying.value = true
  try { await axios.post('/api/music/tracks/' + track.id + '/play') } catch (e) {}
}

function playUserTrack(track) {
  currentTrack.value = { ...track }
  isPlaying.value = true
}

function togglePlay() { isPlaying.value = !isPlaying.value }

function prevTrack() {
  const idx = tracks.value.findIndex(t => t.id === currentTrack.value?.id)
  if (idx > 0) playTrack(tracks.value[idx - 1])
}

function nextTrack() {
  const idx = tracks.value.findIndex(t => t.id === currentTrack.value?.id)
  if (idx < tracks.value.length - 1) playTrack(tracks.value[idx + 1])
}

function openMyPlaylists() {
  showMyPlaylists.value = true
  loadPlaylists()
}

async function loadPlaylists() {
  playlistsLoading.value = true
  try {
    const { data } = await axios.get('/api/music/playlists')
    playlists.value = data
  } catch (e) { playlists.value = [] }
  playlistsLoading.value = false
}

async function createPlaylist() {
  if (!newPlaylistName.value.trim()) return
  try {
    await axios.post('/api/music/playlists', { name: newPlaylistName.value, description: newPlaylistDesc.value })
    newPlaylistName.value = ''
    newPlaylistDesc.value = ''
    showCreatePlaylist.value = false
    await loadPlaylists()
  } catch (e) { alert('생성 실패') }
}

async function deletePlaylist(id) {
  if (!confirm('삭제하시겠습니까?')) return
  try {
    await axios.delete('/api/music/playlists/' + id)
    await loadPlaylists()
  } catch (e) {}
}

async function openPlaylist(pl) {
  try {
    const { data } = await axios.get('/api/music/playlists/' + pl.id)
    activePlaylist.value = data
  } catch (e) {}
}

async function addTrackToPlaylist() {
  if (!addTrackUrl.value.trim()) return
  try {
    await axios.post('/api/music/playlists/' + activePlaylist.value.id + '/tracks', {
      youtube_url: addTrackUrl.value,
    })
    addTrackUrl.value = ''
    await openPlaylist(activePlaylist.value)
  } catch (e) { alert(e.response?.data?.message || '추가 실패') }
}

async function removeTrack(playlistId, trackId) {
  try {
    await axios.delete('/api/music/playlists/' + playlistId + '/tracks/' + trackId)
    await openPlaylist(activePlaylist.value)
  } catch (e) {}
}
</script>

<style scoped>
@keyframes music-bar {
  0%, 100% { height: 4px; }
  50% { height: 20px; }
}
.animate-music-bar {
  animation: music-bar 0.8s ease-in-out infinite;
}
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
