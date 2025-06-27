# debug_tenants.py
# Uruchom: python manage.py shell < debug_tenants.py

print("=" * 60)
print("🔍 DEBUGOWANIE DJANGO-TENANTS")
print("=" * 60)

# 1. Sprawdź czy tabele istnieją
print("\n1. 📋 SPRAWDZENIE TABEL W BAZIE:")
try:
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Sprawdź aktualne połączenie
        cursor.execute("SELECT current_database(), current_schema(), current_user")
        db_info = cursor.fetchone()
        print(f"   Baza: {db_info[0]}")
        print(f"   Schemat: {db_info[1]}")
        print(f"   Użytkownik: {db_info[2]}")
        
        # Sprawdź czy tabele customers istnieją
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename LIKE 'customers_%'
            ORDER BY tablename
        """)
        tables = cursor.fetchall()
        print(f"\n   Tabele customers_*:")
        if tables:
            for table in tables:
                print(f"     ✅ {table[0]}")
        else:
            print("     ❌ BRAK TABEL! Musisz wykonać migracje.")
        
        # Sprawdź wszystkie schematy
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name
        """)
        schemas = [row[0] for row in cursor.fetchall()]
        print(f"\n   Dostępne schematy: {', '.join(schemas)}")
        
except Exception as e:
    print(f"   ❌ BŁĄD: {e}")

# 2. Sprawdź modele
print(f"\n2. 🏗️  SPRAWDZENIE MODELI:")
try:
    from customers.models import Client, Domain
    print("   ✅ Modele zaimportowane poprawnie")
    
    # Spróbuj pobrać dane
    print(f"\n   Próba odczytu z bazy...")
    clients = Client.objects.all()
    print(f"   📊 Liczba tenantów: {clients.count()}")
    
    domains = Domain.objects.all()
    print(f"   📊 Liczba domen: {domains.count()}")
    
    if clients.exists():
        print(f"\n   🏢 TENANTÓW:")
        for client in clients:
            print(f"     - {client.name} (schema: {client.schema_name})")
            client_domains = client.domains.all()
            if client_domains:
                for domain in client_domains:
                    print(f"       🌐 {domain.domain} {'(primary)' if domain.is_primary else ''}")
            else:
                print(f"       ⚠️  Brak domen!")
    else:
        print(f"   ⚠️  BRAK TENANTÓW W BAZIE!")
        
except Exception as e:
    print(f"   ❌ BŁĄD: {e}")
    print(f"   💡 Prawdopodobnie nie wykonałeś migracji!")

# 3. Test konkretnej domeny
print(f"\n3. 🧪 TEST DOMENY 'tenant1.localhost':")
try:
    from customers.models import Domain
    domain = Domain.objects.filter(domain='tenant1.localhost').first()
    
    if domain:
        print(f"   ✅ Domena znaleziona!")
        print(f"   📋 Tenant: {domain.tenant.name}")
        print(f"   📂 Schema: {domain.tenant.schema_name}")
        print(f"   🔑 Primary: {domain.is_primary}")
    else:
        print(f"   ❌ Domena 'tenant1.localhost' NIE ISTNIEJE!")
        print(f"   💡 Musisz ją utworzyć!")
        
except Exception as e:
    print(f"   ❌ BŁĄD: {e}")

# 4. Sprawdź migracje
print(f"\n4. 📦 STATUS MIGRACJI:")
try:
    from django.core.management import execute_from_command_line
    import sys
    from io import StringIO
    
    # Przekieruj stdout żeby przechwycić output
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        execute_from_command_line(['manage.py', 'showmigrations', '--verbosity=0'])
        output = captured_output.getvalue()
        sys.stdout = old_stdout
        
        lines = output.strip().split('\n')
        for line in lines:
            if 'customers' in line:
                print(f"   {line}")
                
    except:
        sys.stdout = old_stdout
        print("   ⚠️  Nie można sprawdzić migracji")
        
except Exception as e:
    print(f"   ❌ BŁĄD: {e}")

print(f"\n" + "=" * 60)
print("🎯 REKOMENDACJE:")

# Sprawdź czy domain exists
domain_exists = False
try:
    from customers.models import Domain
    domain_exists = Domain.objects.filter(domain='tenant1.localhost').exists()
except:
    pass

if not domain_exists:
    print("❌ GŁÓWNY PROBLEM: Brak domeny 'tenant1.localhost'")
    print("\n🔧 KROKI NAPRAWCZE:")
    print("1. python manage.py migrate_schemas")
    print("2. python manage.py shell")
    print("3. Wykonaj kod do tworzenia tenanta (poniżej)")
    print("\n" + "-" * 40)
    print("# W Django shell:")
    print("from customers.models import Client, Domain")
    print("")
    print("# Utwórz tenanta")
    print("tenant = Client.objects.create(")
    print("    name='Test Clinic',")
    print("    schema_name='tenant1'")
    print(")")
    print("")
    print("# Utwórz domenę")
    print("domain = Domain.objects.create(")
    print("    domain='tenant1.localhost',")
    print("    tenant=tenant,")
    print("    is_primary=True")
    print(")")
    print("print(f'Utworzono: {tenant} -> {domain}')")
    print("-" * 40)
else:
    print("✅ Domena istnieje - problem może być gdzie indziej")
    print("💡 Sprawdź czy używasz dokładnie: http://tenant1.localhost:8000/")
    print("💡 Upewnij się, że serwer jest uruchomiony")
    print("💡 Sprawdź logi serwera Django")

print("\n🌐 TESTUJ Z:")
print("http://tenant1.localhost:8000/")
print("http://tenant1.localhost:8000/login/")
print("http://tenant1.localhost:8000/admin/")