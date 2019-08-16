--
-- Name: genetictestfact2; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genetictestfact2 FROM PUBLIC;
REVOKE ALL ON TABLE genetictestfact2 FROM agrbrdf;
GRANT ALL ON TABLE genetictestfact2 TO agrbrdf;
GRANT SELECT ON TABLE genetictestfact2 TO gbs;


