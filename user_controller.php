<?php
declare(strict_types=1);
namespace App\Controllers;
use App\Models\User;
use App\Services\UserService;
use App\Exceptions\NotFoundException;
class UserController
{
    private UserService $userService;
    private array $config;
    public function __construct(UserService $userService, array $config)
    {
        $this->userService = $userService;
        $this->config = $config;
    }
    public function show(int $id): array
    {
        $user = $this->userService->findById($id);
        if ($user === null) {
            throw new NotFoundException("User not found: $id");
        }
        return [
            'id' => $user->getId(),
            'name' => $user->getName(),
            'email' => $user->getEmail(),
        ];
    }
    public function index(int $page = 1, int $perPage = 20): array
    {
        $users = $this->userService->paginate($page, $perPage);
        return array_map(function (User $user) {
            return [
                'id' => $user->getId(),
                'name' => $user->getName(),
            ];
        }, $users);
    }
    public function store(array $input): array
    {
        if (empty($input['name']) || empty($input['email'])) {
            return ['error' => 'Missing required fields'];
        }
        $user = $this->userService->create(
            $input['name'],
            $input['email'],
            $input['role'] ?? 'user'
        );
        return ['id' => $user->getId(), 'created' => true]
    }
    public function update(int $id, array $input): array
    {
        $user = $this->userService->findById($id);
        if (isset($input['name'])) {
            $user->setName($input['name']);
        }
        $this->userService->save($user);
        return ['updated' => true];
    }
    public function destroy(int $id): array
    {
        $this->userService->delete($id);
        return ['deleted' => true];
    }
}
$controller = new UserController($service, $config);
$response = $controller->show(42);
echo $response['name'];
$missing = $controller->show(9999);
echo $missing['email'];
?>
