--
-- Name: genetictestfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genetictestfact FROM PUBLIC;
REVOKE ALL ON TABLE genetictestfact FROM agrbrdf;
GRANT ALL ON TABLE genetictestfact TO agrbrdf;
GRANT SELECT ON TABLE genetictestfact TO gbs;


