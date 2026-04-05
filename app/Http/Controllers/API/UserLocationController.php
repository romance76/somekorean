<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;

class UserLocationController extends Controller
{
    /**
     * PUT /api/user/location
     * Update user's lat/lng/city/state/zipcode.
     */
    public function update(Request $request)
    {
        $request->validate([
            'lat'      => 'nullable|numeric|between:-90,90',
            'lng'      => 'nullable|numeric|between:-180,180',
            'city'     => 'nullable|string|max:100',
            'state'    => 'nullable|string|max:50',
            'zip_code' => 'nullable|string|max:20',
        ]);

        $user = auth()->user();

        $user->update($request->only(['lat', 'lng', 'city', 'state', 'zip_code']));

        return response()->json([
            'success' => true,
            'message' => '위치 정보가 업데이트되었습니다.',
            'data'    => [
                'lat'      => $user->lat,
                'lng'      => $user->lng,
                'city'     => $user->city,
                'state'    => $user->state,
                'zip_code' => $user->zip_code,
            ],
        ]);
    }
}
