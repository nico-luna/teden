<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Servicios Disponibles - Teden</title>
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
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="flex justify-between items-center mb-6">
                <h1 class="text-3xl font-bold text-gray-800">Servicios Disponibles</h1>
                @auth
                    @if(Auth::user()->role === 'seller')
                        <a href="{{ route('appointments.services.create') }}" class="inline-flex items-center px-4 py-2 bg-indigo-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-indigo-700">Ofrecer Nuevo Servicio</a>
                    @endif
                @endauth
            </div>

            <!-- Services Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                @forelse ($services as $service)
                    <a href="{{ route('appointments.services.show', $service) }}" class="block group bg-white rounded-lg shadow-md overflow-hidden transform hover:scale-105 hover:z-10 hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-indigo-500 focus:border-indigo-500 focus:outline-none">
                        <div class="p-4">
                            <h3 class="text-lg font-semibold text-gray-800 group-hover:text-indigo-700">{{ $service->title }}</h3>
                            <p class="text-sm text-gray-600">Ofrecido por: {{ $service->vendor->name }}</p>
                            <p class="mt-2 text-xl font-bold text-indigo-600">${{ number_format($service->price, 2) }}</p>
                            <p class="text-sm text-gray-500">Duración: {{ $service->duration_minutes }} minutos</p>
                            <div class="mt-4">
                                <span class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 group-hover:bg-indigo-200">Ver Detalles</span>
                            </div>
                        </div>
                    </a>
                @empty
                    <div class="col-span-full text-center py-12">
                        <p class="text-gray-500">No hay servicios disponibles en este momento.</p>
                    </div>
                @endforelse
            </div>

            <!-- Pagination -->
            <div class="mt-8">
                {{ $services->links() }}
            </div>
        </div>
    </main>

</body>
</html>
