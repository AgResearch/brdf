--
-- Name: geneticfunctionfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticfunctionfact FROM PUBLIC;
REVOKE ALL ON TABLE geneticfunctionfact FROM agrbrdf;
GRANT ALL ON TABLE geneticfunctionfact TO agrbrdf;
GRANT SELECT ON TABLE geneticfunctionfact TO gbs;


