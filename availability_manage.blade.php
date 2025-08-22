<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestionar Disponibilidad - {{ $service->title }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">

    <!-- Navbar -->
    <nav class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex">
                    <div class="flex-shrink-0 flex items-center">
                        <a href="{{ route('home') }}" class="text-xl font-bold text-indigo-600">Teden</a>
                    </div>
                </div>
                <div class="flex items-center">
                    <a href="{{ route('products.index') }}" class="text-sm font-medium text-gray-500 hover:text-gray-700 mr-4">Marketplace</a>
                    <a href="{{ route('cart.index') }}" class="text-sm font-medium text-gray-500 hover:text-gray-700 mr-4">Carrito</a>
                    <a href="{{ route('orders.index') }}" class="text-sm font-medium text-gray-500 hover:text-gray-700 mr-4">Mis Pedidos</a>
                    @auth
                        <a href="{{ route('home') }}" class="text-sm font-medium text-gray-500 hover:text-gray-700 mr-4">Dashboard</a>
                        <form method="POST" action="{{ route('logout') }}">
                            @csrf
                            <button type="submit" class="text-sm font-medium text-gray-500 hover:text-gray-700">Cerrar Sesión</button>
                        </form>
                    @else
                        <a href="{{ route('login') }}" class="text-sm font-medium text-gray-500 hover:text-gray-700 mr-4">Iniciar Sesión</a>
                        <a href="{{ route('register') }}" class="text-sm font-medium text-gray-500 hover:text-gray-700">Registrarse</a>
                    @endauth
                </div>
            </div>
        </div>
    </nav>

    <!-- Page Content -->
    <main class="py-10">
        <div class="max-w-3xl mx-auto sm:px-6 lg:px-8">
            <h1 class="text-3xl font-bold text-gray-800 mb-6">Gestionar Disponibilidad para: {{ $service->title }}</h1>

            @if (session('success'))
                <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
                    <span class="block sm:inline">{{ session('success') }}</span>
                </div>
            @endif

            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg p-6">
                <h2 class="text-xl font-semibold text-gray-800 mb-4">Añadir Nueva Disponibilidad</h2>
                <form method="POST" action="{{ route('appointments.availability.store', $service) }}" class="space-y-6">
                    @csrf

                    <!-- Weekday -->
                    <div>
                        <label for="weekday" class="block text-sm font-medium text-gray-700">Día de la Semana</label>
                        <select id="weekday" name="weekday" required class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
                            <option value="0">Lunes</option>
                            <option value="1">Martes</option>
                            <option value="2">Miércoles</option>
                            <option value="3">Jueves</option>
                            <option value="4">Viernes</option>
                            <option value="5">Sábado</option>
                            <option value="6">Domingo</option>
                        </select>
                        @error('weekday') <p class="text-red-500 text-xs mt-1">{{ $message }}</p> @enderror
                    </div>

                    <!-- Start Time -->
                    <div>
                        <label for="start_time" class="block text-sm font-medium text-gray-700">Hora de Inicio</label>
                        <input id="start_time" type="time" name="start_time" value="{{ old('start_time') }}" required class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                        @error('start_time') <p class="text-red-500 text-xs mt-1">{{ $message }}</p> @enderror
                    </div>

                    <!-- End Time -->
                    <div>
                        <label for="end_time" class="block text-sm font-medium text-gray-700">Hora de Fin</label>
                        <input id="end_time" type="time" name="end_time" value="{{ old('end_time') }}" required class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                        @error('end_time') <p class="text-red-500 text-xs mt-1">{{ $message }}</p> @enderror
                    </div>

                    <div class="flex justify-end pt-6 border-t border-gray-200">
                        <button type="submit" class="inline-flex items-center px-4 py-2 bg-indigo-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-indigo-700 active:bg-indigo-900 focus:outline-none focus:border-indigo-900 focus:ring ring-indigo-300 disabled:opacity-25 transition ease-in-out duration-150">
                            Añadir Disponibilidad
                        </button>
                    </div>
                </form>
            </div>

            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg p-6 mt-8">
                <h2 class="text-xl font-semibold text-gray-800 mb-4">Disponibilidades Actuales</h2>
                @if ($slots->isEmpty())
                    <p class="text-gray-600">No hay disponibilidades configuradas para este servicio.</p>
                @else
                    <ul class="divide-y divide-gray-200">
                        @foreach ($slots as $slot)
                            <li class="py-4 flex justify-between items-center">
                                <div>
                                    <p class="font-medium text-gray-900">{{ ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][$slot->weekday] }}</p>
                                    <p class="text-sm text-gray-600">{{ 
Carbon
::parse($slot->start_time)->format('H:i') }} - {{ 
Carbon
::parse($slot->end_time)->format('H:i') }}</p>
                                </div>
                                <form action="{{ route('appointments.availability.destroy', $slot) }}" method="POST" onsubmit="return confirm('¿Estás seguro de que quieres eliminar esta disponibilidad?');">
                                    @csrf
                                    @method('DELETE')
                                    <button type="submit" class="text-sm font-medium text-red-600 hover:text-red-900">Eliminar</button>
                                </form>
                            </li>
                        @endforeach
                    </ul>
                @endif
            </div>
        </div>
    </main>

</body>
</html>
