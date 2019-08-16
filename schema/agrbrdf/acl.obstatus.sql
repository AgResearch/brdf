--
-- Name: obstatus; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE obstatus FROM PUBLIC;
REVOKE ALL ON TABLE obstatus FROM agrbrdf;
GRANT ALL ON TABLE obstatus TO agrbrdf;
GRANT SELECT ON TABLE obstatus TO gbs;


