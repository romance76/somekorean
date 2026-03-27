<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Board;

class BoardController extends Controller
{
    public function index()
    {
        $boards = Board::where('is_active', true)
            ->orderBy('sort_order')
            ->get();
        return response()->json($boards);
    }

    public function show(Board $board)
    {
        return response()->json($board);
    }
}
