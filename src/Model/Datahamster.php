<?php
namespace PIM;

class Model_Datahamster extends Model_Persistable {

    /**
     *
     * @var <type>
     */
    private static $tablename = 'datahamster';

    /**
     *
     * @var Model_Address|int
     */
    private $address;

    /**
     *
     * @var Model_Category|int
     */
    private $category;

    /**
     *
     * @var Model_Datahamster|int
     */
    private $parent;

    /**
     *
     * @var string
     */
    private $name;

    /**
     *
     * @var string
     */
    private $department;

    /**
     *
     * @var string
     */
    private $web;

    /**
     *
     * @var string
     */
    private $email;

    /**
     * Constructor
     * @param int $id
     */
    public function __construct( $id = null ) {
        parent::__construct( $id );
    }

    /**
     * Destructor
     */
    public function __destruct() {
        parent::__destruct();
    }

    /**
     *
     * @return Model_Address
     */
    public function getAddress() {
        if (\is_numeric( $this->address ) ) {
            $this->address = Model_Address::findById( $this->address );
        }
        return $this->address;
    }

    /**
     *
     * @return Model_Category
     */
    public function getCategory() {
        if ( \is_numeric( $this->category ) ) {
            $this->category = Model_Category::findById( $this->category );
        }
        return $this->category;
    }

    /**
     *
     * @return Model_Datahamster
     */
    public function getParent() {
        if ( \is_numeric( $this->parent ) ) {
            $this->parent = Model_Datahamster::findById( $this->parent );
        }
        return $this->parent;
    }

    /**
     *
     * @return string
     */
    public function getName() {
        return $this->name;
    }

    /**
     *
     * @return string
     */
    public function getDepartment() {
        return $this->department;
    }

    /**
     *
     * @return string
     */
    public function getWeb() {
        return $this->web;
    }

    /**
     *
     * @return string
     */
    public function getEmail() {
        return $this->email;
    }

    /**
     *
     * @param Model_Address|int $address
     */
    public function setAddress( $address ) {
        $this->address = $address;
    }

    /**
     *
     * @param Model_Category|int $category
     */
    public function setCategory( $category ) {
        $this->category = $category;
    }

    /**
     *
     * @param Model_Datahamster|int $parent
     */
    public function setParent( $parent ) {
        $this->parent = $parent;
    }

    /**
     *
     * @param string $name
     */
    public function setName( $name ) {
        $this->name = $name;
    }

    /**
     *
     * @param string $department
     */
    public function setDepartment( $department ) {
        $this->department = $department;
    }

    /**
     *
     * @param string $web
     */
    public function setWeb( $web ) {
        $this->web = $web;
    }

    /**
     *
     * @param string $email
     */
    public function setEmail( $email ) {
        $this->email = $email;
    }

    /**
     * @return bool
     */
    public function insert() {
        if ( !\is_null( $this->id ) ) {
            return false;
        }

        $prep_query = "INSERT INTO `" . self::$tablename . "` " .
            "(address_id, category_id, parent_id, name, department, web, email) " .
            "VALUES (?, ?, ?, ?, ?, ?, ?)";

        $connection = self::getConnection();

        if ( !\is_null( $connection ) ) {
            $stmt = $connection->prepare( $prep_query );

            $address_id = ( $this->address instanceof Model_Address )
                    ? $this->address->getId() : $this->address;
            $category_id = ($this->category instanceof Model_Category )
                    ? $this->category->getId() : $this->category;
            $parent_id = ( $this->parent instanceof Model_Datahamster )
                    ? $this->parent->getId() : $this->parent;

            if ( $stmt->bind_param( "iiissss", $address_id, $category_id
                    , $parent_id, $this->name, $this->department, $this->web
                    , $this->email ) ) {

                $result = $stmt->execute();

                if ( $result === true ) {
                    $this->id = $stmt->insert_id;
                }
                $stmt->close();
                return $result;
            }
        }

        return false;
    }

    /**
     * @return bool
     */
    public function update() {
        if ( \is_null( $this->id ) ) {
            return false;
        }

        $prep_query = "UPDATE `" . self::$tablename . "` " .
            "SET address_id = ?, categpry_id = ? , parent_id = ?" .
            ", name = ?, department = ?, web = ?, email = ?" .
            "WHERE id = ?";

        $connection = self::getConnection();

        if ( !\is_null( $connection ) ) {
            $stmt = $connection->prepare( $prep_query );

            $address_id = ( $this->address instanceof Model_Address )
                    ? $this->address->getId() : $this->address;
            $category_id = ($this->category instanceof Model_Category )
                    ? $this->category->getId() : $this->category;
            $parent_id = ( $this->parent instanceof Model_Datahamster )
                    ? $this->parent->getId() : $this->parent;

            if ( $stmt->bind_param( "iiissssi", $address_id, $category_id
                    , $parent_id, $this->name, $this->department, $this->web
                    , $this->email, $this->id ) ) {

                $result = $stmt->execute();
                $stmt->close();
                return $result;
            }
        }

        return false;
    }

    /**
     * @return bool
     */
    public function delete() {
        if ( \is_null( $this->id ) ) {
            return false;
        }

        $prep_query = "DELETE FROM `" . self::$tablename . "` " .
            "WHERE id = ?";

        $connection = self::getConnection();

        if ( !\is_null( $connection ) ) {
            $stmt = $connection->prepare( $prep_query );

            if ( $stmt->bind_param( "i", $this->id ) ) {

                $result = $stmt->execute();

                if ( $result === true ) {
                    $this->id = null;
                }

                $stmt->close();
                return $result;
            }
        }

        return false;
    }

    /**
     *
     * @param int $id
     * @return Model_Datahamster
     */
    public static function findById( $id ) {
        $prep_query = "SELECT address_id, category_id, parent_id, name " .
            ", department, web, email " .
            "FROM `" . self::$tablename . "` " .
            "WHERE id = ?";

        $connection = self::getConnection();
        $datahamster = null;

        if ( !\is_null( $connection ) ) {
            $stmt = $connection->prepare( $prep_query );

            if ( $stmt->bind_param( "i", $id ) ) {

                $result = $stmt->execute();

                if ( $result === true ) {

                    if ( $stmt->bind_result( $address_id, $category_id,
                            $parent_id, $name, $department, $web, $email ) ) {

                        if ( $stmt->fetch() ) {
                            $datahamster = new Model_Datahamster( $id );
                            $datahamster->setAddress( $address_id );
                            $datahamster->setCategory( $category_id );
                            $datahamster->setDepartment( $department_id );
                            $datahamster->setEmail( $email );
                            $datahamster->setName( $name );
                            $datahamster->setParent( $parent_id );
                            $datahamster->setWeb( $web );
                        }

                    }

                }
                $stmt->close();
            }
        }

        return $datahamster;
    }
}