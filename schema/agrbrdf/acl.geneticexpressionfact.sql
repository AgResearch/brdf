--
-- Name: geneticexpressionfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticexpressionfact FROM PUBLIC;
REVOKE ALL ON TABLE geneticexpressionfact FROM agrbrdf;
GRANT ALL ON TABLE geneticexpressionfact TO agrbrdf;
GRANT SELECT ON TABLE geneticexpressionfact TO gbs;


