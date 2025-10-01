# Smart Backend Methods - Continue the implementation

def _generate_smart_security_services(self):
    """Generate smart security services for form protection"""
    
    template = Template("""<?php

namespace App\Services;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Hash;

class SmartSecurityService
{
    /**
     * Device fingerprinting and recognition
     */
    public function getDeviceFingerprint(Request $request): string
    {
        $components = [
            $request->userAgent(),
            $request->ip(),
            $request->header('Accept-Language'),
            $request->header('Accept-Encoding'),
            $request->header('Accept')
        ];
        
        return hash('sha256', implode('|', array_filter($components)));
    }
    
    /**
     * Check for suspicious device activity
     */
    public function checkDeviceActivity(Request $request, $userId): array
    {
        $fingerprint = $this->getDeviceFingerprint($request);
        $cacheKey = "device_activity:{$userId}:{$fingerprint}";
        
        $activity = Cache::get($cacheKey, [
            'first_seen' => now(),
            'login_count' => 0,
            'last_login' => null,
            'is_trusted' => false
        ]);
        
        $isNewDevice = $activity['login_count'] === 0;
        $activity['login_count']++;
        $activity['last_login'] = now();
        
        // Trust device after 3 successful logins
        if ($activity['login_count'] >= 3) {
            $activity['is_trusted'] = true;
        }
        
        Cache::put($cacheKey, $activity, 86400 * 30); // 30 days
        
        return [
            'is_new_device' => $isNewDevice,
            'is_trusted' => $activity['is_trusted'],
            'login_count' => $activity['login_count'],
            'fingerprint' => $fingerprint
        ];
    }
    
    /**
     * Rate limiting for form submissions
     */
    public function checkRateLimit(Request $request, string $action, int $maxAttempts = 5, int $decayMinutes = 15): array
    {
        $key = $this->getRateLimitKey($request, $action);
        $attempts = Cache::get($key, 0);
        
        if ($attempts >= $maxAttempts) {
            $retryAfter = Cache::get($key . ':expires', 0) - time();
            return [
                'allowed' => false,
                'attempts' => $attempts,
                'max_attempts' => $maxAttempts,
                'retry_after' => max(0, $retryAfter)
            ];
        }
        
        return [
            'allowed' => true,
            'attempts' => $attempts,
            'max_attempts' => $maxAttempts,
            'retry_after' => 0
        ];
    }
    
    /**
     * Record rate limit attempt
     */
    public function recordAttempt(Request $request, string $action, int $decayMinutes = 15): void
    {
        $key = $this->getRateLimitKey($request, $action);
        $attempts = Cache::get($key, 0) + 1;
        
        Cache::put($key, $attempts, $decayMinutes * 60);
        Cache::put($key . ':expires', time() + ($decayMinutes * 60), $decayMinutes * 60);
    }
    
    /**
     * Fraud detection for suspicious patterns
     */
    public function detectFraud(array $formData, Request $request): array
    {
        $suspiciousFlags = [];
        $riskScore = 0;
        
        // Check for rapid form completion (too fast for human)
        if (isset($formData['_form_start_time'])) {
            $completionTime = time() - $formData['_form_start_time'];
            if ($completionTime < 5) { // Less than 5 seconds
                $suspiciousFlags[] = 'rapid_completion';
                $riskScore += 30;
            }
        }
        
        // Check for suspicious patterns in data
        foreach ($formData as $field => $value) {
            if (is_string($value)) {
                // Check for repeated characters
                if (preg_match('/(.)\1{5,}/', $value)) {
                    $suspiciousFlags[] = 'repeated_characters';
                    $riskScore += 10;
                }
                
                // Check for keyboard patterns
                if ($this->isKeyboardPattern($value)) {
                    $suspiciousFlags[] = 'keyboard_pattern';
                    $riskScore += 15;
                }
            }
        }
        
        // Check IP reputation
        $ipReputation = $this->checkIPReputation($request->ip());
        if ($ipReputation['is_suspicious']) {
            $suspiciousFlags[] = 'suspicious_ip';
            $riskScore += $ipReputation['risk_score'];
        }
        
        // Determine risk level
        $riskLevel = 'low';
        if ($riskScore >= 50) $riskLevel = 'high';
        elseif ($riskScore >= 25) $riskLevel = 'medium';
        
        return [
            'risk_score' => $riskScore,
            'risk_level' => $riskLevel,
            'flags' => $suspiciousFlags,
            'action' => $this->getRecommendedAction($riskLevel)
        ];
    }
    
    /**
     * Generate honeypot fields for bot detection
     */
    public function generateHoneypot(): array
    {
        $fields = [
            'website_url', 'company_name', 'phone_number', 
            'email_address', 'full_name', 'street_address'
        ];
        
        $honeypotField = $fields[array_rand($fields)];
        $honeypotToken = bin2hex(random_bytes(16));
        
        Cache::put("honeypot:{$honeypotToken}", $honeypotField, 3600);
        
        return [
            'field_name' => $honeypotField,
            'token' => $honeypotToken
        ];
    }
    
    /**
     * Validate honeypot submission
     */
    public function validateHoneypot(array $formData): bool
    {
        foreach ($formData as $field => $value) {
            if (str_starts_with($field, 'honeypot_')) {
                $token = substr($field, 9);
                $expectedField = Cache::get("honeypot:{$token}");
                
                if ($expectedField && !empty($value)) {
                    // Bot detected - filled honeypot field
                    Log::warning('Honeypot triggered', [
                        'field' => $field,
                        'value' => $value,
                        'ip' => request()->ip(),
                        'user_agent' => request()->userAgent()
                    ]);
                    return false;
                }
            }
        }
        
        return true;
    }
    
    // Private helper methods
    
    private function getRateLimitKey(Request $request, string $action): string
    {
        return sprintf(
            'rate_limit:%s:%s:%s',
            $action,
            $request->ip(),
            $request->userAgent() ? hash('md5', $request->userAgent()) : 'unknown'
        );
    }
    
    private function isKeyboardPattern(string $value): bool
    {
        $patterns = [
            'qwerty', 'asdf', 'zxcv', '1234', 'abcd',
            'qwertyuiop', 'asdfghjkl', 'zxcvbnm'
        ];
        
        foreach ($patterns as $pattern) {
            if (stripos($value, $pattern) !== false) {
                return true;
            }
        }
        
        return false;
    }
    
    private function checkIPReputation(string $ip): array
    {
        // This would integrate with IP reputation services
        $cacheKey = "ip_reputation:{$ip}";
        
        return Cache::remember($cacheKey, 3600, function () use ($ip) {
            // Placeholder for actual IP reputation check
            return [
                'is_suspicious' => false,
                'risk_score' => 0,
                'reasons' => []
            ];
        });
    }
    
    private function getRecommendedAction(string $riskLevel): string
    {
        return match($riskLevel) {
            'high' => 'block',
            'medium' => 'challenge',
            'low' => 'allow',
            default => 'allow'
        };
    }
}
""")
    
    service_content = template.render()
    
    services_dir = self.backend_path / "app" / "Services"
    service_file = services_dir / "SmartSecurityService.php"
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    return service_content

def _generate_smart_form_controller(self):
    """Generate smart form controller with validation endpoints"""
    
    template = Template("""<?php

namespace App\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Validator;
use App\Services\SmartValidationService;
use App\Services\SmartSecurityService;

class SmartFormController
{
    private $validationService;
    private $securityService;
    
    public function __construct(
        SmartValidationService $validationService,
        SmartSecurityService $securityService
    ) {
        $this->validationService = $validationService;
        $this->securityService = $securityService;
    }
    
    /**
     * Validate individual field in real-time
     */
    public function validateField(Request $request): JsonResponse
    {
        $fieldType = $request->input('type');
        $fieldValue = $request->input('value');
        $fieldOptions = $request->input('options', []);
        
        $result = match($fieldType) {
            'email' => $this->validationService->validateEmail($fieldValue, $fieldOptions),
            'phone' => $this->validationService->validatePhone($fieldValue, $fieldOptions),
            'password' => $this->validationService->validatePasswordStrength($fieldValue),
            'otp' => $this->validationService->validateOTP($fieldValue, $request->input('identifier'), $fieldOptions),
            default => ['valid' => true, 'errors' => [], 'suggestions' => []]
        };
        
        return response()->json($result);
    }
    
    /**
     * Get smart suggestions for form fields
     */
    public function getFieldSuggestions(Request $request): JsonResponse
    {
        $fieldType = $request->input('type');
        $query = $request->input('query', '');
        $context = $request->input('context', []);
        
        $suggestions = [];
        
        switch ($fieldType) {
            case 'country':
                $suggestions = $this->getCountrySuggestions($query);
                break;
            case 'city':
                $suggestions = $this->getCitySuggestions($query, $context['country'] ?? null);
                break;
            case 'address':
                $suggestions = $this->getAddressSuggestions($query);
                break;
            case 'company':
                $suggestions = $this->getCompanySuggestions($query);
                break;
            default:
                $suggestions = [];
        }
        
        return response()->json(['suggestions' => $suggestions]);
    }
    
    /**
     * Auto-fill known user data
     */
    public function getAutofillData(Request $request): JsonResponse
    {
        $user = $request->user();
        $fields = $request->input('fields', []);
        
        $autofillData = [];
        
        if ($user) {
            foreach ($fields as $field) {
                switch ($field) {
                    case 'email':
                        $autofillData['email'] = $user->email;
                        break;
                    case 'phone':
                        $autofillData['phone'] = $user->phone;
                        break;
                    case 'name':
                        $autofillData['name'] = $user->name;
                        break;
                    case 'address':
                        if ($user->address) {
                            $autofillData['address'] = json_decode($user->address, true);
                        }
                        break;
                }
            }
        }
        
        return response()->json(['data' => $autofillData]);
    }
    
    /**
     * Check form security and fraud detection
     */
    public function checkFormSecurity(Request $request): JsonResponse
    {
        // Check rate limiting
        $rateLimitResult = $this->securityService->checkRateLimit($request, 'form_submission');
        if (!$rateLimitResult['allowed']) {
            return response()->json([
                'allowed' => false,
                'reason' => 'rate_limit_exceeded',
                'retry_after' => $rateLimitResult['retry_after']
            ], 429);
        }
        
        // Validate honeypot
        $honeypotValid = $this->securityService->validateHoneypot($request->all());
        if (!$honeypotValid) {
            return response()->json([
                'allowed' => false,
                'reason' => 'bot_detected'
            ], 422);
        }
        
        // Fraud detection
        $fraudResult = $this->securityService->detectFraud($request->all(), $request);
        
        // Device activity check
        $deviceResult = [];
        if ($request->user()) {
            $deviceResult = $this->securityService->checkDeviceActivity($request, $request->user()->id);
        }
        
        return response()->json([
            'allowed' => $fraudResult['action'] !== 'block',
            'fraud_check' => $fraudResult,
            'device_check' => $deviceResult,
            'security_level' => $this->getSecurityLevel($fraudResult, $deviceResult)
        ]);
    }
    
    /**
     * Save form draft
     */
    public function saveDraft(Request $request): JsonResponse
    {
        $formId = $request->input('form_id');
        $formData = $request->input('data', []);
        $userId = $request->user()?->id ?? session()->getId();
        
        $draftKey = "form_draft:{$formId}:{$userId}";
        
        cache()->put($draftKey, [
            'data' => $formData,
            'saved_at' => now()->toISOString()
        ], 3600); // 1 hour
        
        return response()->json([
            'success' => true,
            'message' => 'Draft saved successfully'
        ]);
    }
    
    /**
     * Get form draft
     */
    public function getDraft(Request $request): JsonResponse
    {
        $formId = $request->input('form_id');
        $userId = $request->user()?->id ?? session()->getId();
        
        $draftKey = "form_draft:{$formId}:{$userId}";
        $draft = cache()->get($draftKey);
        
        return response()->json([
            'draft' => $draft
        ]);
    }
    
    /**
     * Generate honeypot fields
     */
    public function getHoneypot(Request $request): JsonResponse
    {
        $honeypot = $this->securityService->generateHoneypot();
        
        return response()->json($honeypot);
    }
    
    // Private helper methods
    
    private function getCountrySuggestions(string $query): array
    {
        $countries = [
            'United States', 'Canada', 'United Kingdom', 'Australia',
            'Germany', 'France', 'Japan', 'India', 'Brazil', 'Mexico'
        ];
        
        return array_filter($countries, function($country) use ($query) {
            return stripos($country, $query) !== false;
        });
    }
    
    private function getCitySuggestions(string $query, ?string $country): array
    {
        // This would typically integrate with a geocoding service
        $cities = [
            'New York', 'Los Angeles', 'Chicago', 'Toronto', 'London',
            'Paris', 'Berlin', 'Tokyo', 'Mumbai', 'Sydney'
        ];
        
        return array_filter($cities, function($city) use ($query) {
            return stripos($city, $query) !== false;
        });
    }
    
    private function getAddressSuggestions(string $query): array
    {
        // This would integrate with Google Places API or similar
        return [];
    }
    
    private function getCompanySuggestions(string $query): array
    {
        // This would integrate with a company database
        return [];
    }
    
    private function getSecurityLevel(array $fraudResult, array $deviceResult): string
    {
        if ($fraudResult['risk_level'] === 'high' || !empty($deviceResult['is_new_device'])) {
            return 'high';
        } elseif ($fraudResult['risk_level'] === 'medium') {
            return 'medium';
        }
        
        return 'low';
    }
}
""")
    
    controller_content = template.render()
    
    controller_file = self.backend_path / "app" / "Controllers" / "SmartFormController.php"
    with open(controller_file, 'w') as f:
        f.write(controller_content)
    
    return controller_content

def _generate_field_validation_rules(self):
    """Generate custom field validation rules"""
    
    template = Template("""<?php

namespace App\Rules;

use Illuminate\Contracts\Validation\Rule;
use App\Services\SmartValidationService;

class SmartEmailRule implements Rule
{
    private $options;
    private $validationService;
    
    public function __construct(array $options = [])
    {
        $this->options = $options;
        $this->validationService = app(SmartValidationService::class);
    }
    
    public function passes($attribute, $value)
    {
        $result = $this->validationService->validateEmail($value, $this->options);
        return $result['valid'];
    }
    
    public function message()
    {
        return 'The :attribute is not a valid email address.';
    }
}

class SmartPhoneRule implements Rule
{
    private $options;
    private $validationService;
    
    public function __construct(array $options = [])
    {
        $this->options = $options;
        $this->validationService = app(SmartValidationService::class);
    }
    
    public function passes($attribute, $value)
    {
        $result = $this->validationService->validatePhone($value, $this->options);
        return $result['valid'];
    }
    
    public function message()
    {
        return 'The :attribute is not a valid phone number.';
    }
}

class PasswordStrengthRule implements Rule
{
    private $minScore;
    private $validationService;
    
    public function __construct(int $minScore = 3)
    {
        $this->minScore = $minScore;
        $this->validationService = app(SmartValidationService::class);
    }
    
    public function passes($attribute, $value)
    {
        $result = $this->validationService->validatePasswordStrength($value);
        return $result['score'] >= $this->minScore;
    }
    
    public function message()
    {
        return 'The :attribute is not strong enough.';
    }
}
""")
    
    rules_content = template.render()
    
    rules_dir = self.backend_path / "app" / "Rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    rules_file = rules_dir / "SmartValidationRules.php"
    with open(rules_file, 'w') as f:
        f.write(rules_content)
    
    return rules_content

def _generate_validation_middleware(self):
    """Generate validation middleware for smart forms"""
    
    template = Template("""<?php

namespace App\Middleware;

use Closure;
use Illuminate\Http\Request;
use App\Services\SmartSecurityService;

class SmartFormValidationMiddleware
{
    private $securityService;
    
    public function __construct(SmartSecurityService $securityService)
    {
        $this->securityService = $securityService;
    }
    
    public function handle(Request $request, Closure $next)
    {
        // Skip validation for GET requests
        if ($request->isMethod('GET')) {
            return $next($request);
        }
        
        // Check rate limiting
        $rateLimitResult = $this->securityService->checkRateLimit(
            $request, 
            'form_submission'
        );
        
        if (!$rateLimitResult['allowed']) {
            return response()->json([
                'error' => 'Rate limit exceeded',
                'retry_after' => $rateLimitResult['retry_after']
            ], 429);
        }
        
        // Record the attempt
        $this->securityService->recordAttempt($request, 'form_submission');
        
        // Validate honeypot
        if (!$this->securityService->validateHoneypot($request->all())) {
            return response()->json([
                'error' => 'Security validation failed'
            ], 422);
        }
        
        // Fraud detection
        $fraudResult = $this->securityService->detectFraud($request->all(), $request);
        
        if ($fraudResult['action'] === 'block') {
            return response()->json([
                'error' => 'Request blocked due to suspicious activity',
                'risk_score' => $fraudResult['risk_score']
            ], 403);
        }
        
        // Add security context to request
        $request->merge([
            '_security_context' => [
                'fraud_result' => $fraudResult,
                'device_fingerprint' => $this->securityService->getDeviceFingerprint($request)
            ]
        ]);
        
        return $next($request);
    }
}
""")
    
    middleware_content = template.render()
    
    middleware_dir = self.backend_path / "app" / "Middleware"
    middleware_dir.mkdir(parents=True, exist_ok=True)
    
    middleware_file = middleware_dir / "SmartFormValidationMiddleware.php"
    with open(middleware_file, 'w') as f:
        f.write(middleware_content)
    
    return middleware_content

def _generate_smart_search_autocomplete_service(self):
    """Generate smart search and autocomplete service"""
    
    template = Template("""<?php

namespace App\Services;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class SmartSearchService
{
    protected $searchProviders = [
        'local' => true,
        'elasticsearch' => false,
        'algolia' => false,
        'google_places' => true
    ];
    
    /**
     * Perform intelligent search with typo tolerance
     */
    public function search(string $query, array $options = []): array
    {
        $searchType = $options['search_type'] ?? 'general';
        $maxResults = $options['max_results'] ?? 10;
        $enableTypoTolerance = $options['enable_typo_tolerance'] ?? true;
        $contextFilters = $options['context_filters'] ?? [];
        
        $cacheKey = \"search:{$searchType}:\" . md5($query . serialize($contextFilters));
        
        return Cache::remember($cacheKey, 300, function () use ($query, $searchType, $maxResults, $enableTypoTolerance, $contextFilters) {
            $results = [];
            $hasTypoCorrection = false;
            
            // Local database search
            if ($this->searchProviders['local']) {
                $localResults = $this->searchLocal($query, $searchType, $contextFilters);
                $results = array_merge($results, $localResults);
            }
            
            // External search providers
            if ($searchType === 'places' || $searchType === 'address') {
                $placesResults = $this->searchGooglePlaces($query, $contextFilters);
                $results = array_merge($results, $placesResults);
            }
            
            // Typo tolerance
            if ($enableTypoTolerance && empty($results)) {
                $correctedQuery = $this->correctTypos($query);
                if ($correctedQuery !== $query) {
                    $correctedResults = $this->search($correctedQuery, array_merge($options, ['enable_typo_tolerance' => false]));
                    $results = $correctedResults['suggestions'] ?? [];
                    $hasTypoCorrection = true;
                }
            }
            
            // Score and sort results
            $scoredResults = $this->scoreResults($results, $query);
            $topResults = array_slice($scoredResults, 0, $maxResults);
            
            return [
                'suggestions' => $topResults,
                'has_typo_correction' => $hasTypoCorrection,
                'original_query' => $query,
                'corrected_query' => $correctedQuery ?? null,
                'total_results' => count($results)
            ];
        });
    }
    
    /**
     * Get autocomplete suggestions for specific field types
     */
    public function getFieldSuggestions(string $fieldType, string $query, array $options = []): array
    {
        switch ($fieldType) {
            case 'email':
                return $this->getEmailSuggestions($query, $options);
            case 'country':
                return $this->getCountrySuggestions($query, $options);
            case 'city':
                return $this->getCitySuggestions($query, $options);
            case 'company':
                return $this->getCompanySuggestions($query, $options);
            default:
                return $this->search($query, array_merge($options, ['search_type' => $fieldType]));
        }
    }
    
    /**
     * Search local database
     */
    protected function searchLocal(string $query, string $searchType, array $contextFilters): array
    {
        $results = [];
        
        try {
            switch ($searchType) {
                case 'users':
                    $users = DB::table('users')
                        ->where('name', 'LIKE', \"%{$query}%\")
                        ->orWhere('email', 'LIKE', \"%{$query}%\")
                        ->limit(20)
                        ->get();
                    
                    foreach ($users as $user) {
                        $results[] = [
                            'text' => $user->name,
                            'description' => $user->email,
                            'type' => 'user',
                            'id' => $user->id,
                            'category' => 'Users'
                        ];
                    }
                    break;
                    
                case 'general':
                default:
                    // Search across multiple tables
                    $tables = ['users', 'posts', 'products', 'categories'];
                    
                    foreach ($tables as $table) {
                        if (DB::getSchemaBuilder()->hasTable($table)) {
                            $tableResults = DB::table($table)
                                ->where(function ($query_builder) use ($query) {
                                    $columns = DB::getSchemaBuilder()->getColumnListing($query_builder->from);
                                    foreach (['name', 'title', 'description', 'content'] as $searchColumn) {
                                        if (in_array($searchColumn, $columns)) {
                                            $query_builder->orWhere($searchColumn, 'LIKE', \"%{$query}%\");
                                        }
                                    }
                                })
                                ->limit(5)
                                ->get();
                            
                            foreach ($tableResults as $result) {
                                $results[] = [
                                    'text' => $result->name ?? $result->title ?? 'Result',
                                    'description' => $result->description ?? null,
                                    'type' => $table,
                                    'id' => $result->id,
                                    'category' => ucfirst($table)
                                ];
                            }
                        }
                    }
                    break;
            }
        } catch (\\Exception $e) {
            Log::error('Local search error: ' . $e->getMessage());
        }
        
        return $results;
    }
    
    /**
     * Email domain suggestions
     */
    protected function getEmailSuggestions(string $query, array $options): array
    {
        if (!str_contains($query, '@')) {
            return ['suggestions' => []];
        }
        
        [$localPart, $domain] = explode('@', $query, 2);
        
        $commonDomains = [
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
            'icloud.com', 'aol.com', 'live.com', 'msn.com'
        ];
        
        $suggestions = [];
        
        foreach ($commonDomains as $commonDomain) {
            if (str_starts_with($commonDomain, $domain)) {
                $suggestions[] = [
                    'text' => $localPart . '@' . $commonDomain,
                    'type' => 'email_suggestion',
                    'description' => 'Common email domain'
                ];
            }
        }
        
        return ['suggestions' => array_slice($suggestions, 0, 5)];
    }
    
    /**
     * Country suggestions
     */
    protected function getCountrySuggestions(string $query, array $options): array
    {
        $countries = [
            'United States', 'United Kingdom', 'Canada', 'Australia',
            'Germany', 'France', 'Italy', 'Spain', 'Netherlands',
            'Sweden', 'Norway', 'Denmark', 'Finland', 'Japan',
            'China', 'India', 'Brazil', 'Mexico', 'Nigeria', 'South Africa'
        ];
        
        $suggestions = [];
        $queryLower = strtolower($query);
        
        foreach ($countries as $country) {
            if (str_contains(strtolower($country), $queryLower)) {
                $suggestions[] = [
                    'text' => $country,
                    'type' => 'country',
                    'category' => 'Countries'
                ];
            }
        }
        
        return ['suggestions' => array_slice($suggestions, 0, 10)];
    }
    
    /**
     * Typo correction using common patterns
     */
    protected function correctTypos(string $query): string
    {
        $commonTypos = [
            'teh' => 'the',
            'adn' => 'and',
            'recieve' => 'receive',
            'laos' => 'lagos', // Common geographic typo
            'newyork' => 'new york',
            '@gmai.com' => '@gmail.com',
            '@yahoo.co' => '@yahoo.com'
        ];
        
        $corrected = $query;
        
        foreach ($commonTypos as $typo => $correction) {
            $corrected = str_ireplace($typo, $correction, $corrected);
        }
        
        return $corrected;
    }
    
    /**
     * Score search results based on relevance
     */
    protected function scoreResults(array $results, string $query): array
    {
        foreach ($results as &$result) {
            $score = 0;
            $text = strtolower($result['text'] ?? '');
            $queryLower = strtolower($query);
            
            // Exact match gets highest score
            if ($text === $queryLower) {
                $score += 100;
            }
            // Starts with query
            elseif (str_starts_with($text, $queryLower)) {
                $score += 80;
            }
            // Contains query
            elseif (str_contains($text, $queryLower)) {
                $score += 60;
            }
            
            $result['relevance_score'] = $score;
        }
        
        // Sort by relevance score descending
        usort($results, function ($a, $b) {
            return ($b['relevance_score'] ?? 0) - ($a['relevance_score'] ?? 0);
        });
        
        return $results;
    }
}
\"\"\")
    
    service_content = template.render()
    
    service_file = self.backend_path / "app" / "Services" / "SmartSearchService.php"
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    return service_content